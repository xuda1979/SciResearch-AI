from __future__ import annotations

import time

from .config import RunConfig
from .inference import debate, reflection, ttc


class Orchestrator:
    def __init__(self, project, provider, cfg: RunConfig):
        self.project = project
        self.provider = provider
        self.cfg = cfg
        self.stop_flag = False

    def _gen(self, prompt: str, n: int = 1):
        return self.provider.generate(prompt, n=n)

    def _score(self, text: str) -> float:
        # heuristic scoring placeholder: prefer longer, structured answers
        return min(1.0, 0.2 + 0.0005 * len(text)) + text.count("\n") * 0.01

    def run(self):
        pm = self.project.pm
        state = {"iter": 0, "status": "running"}
        start = time.time()
        while state["iter"] < self.cfg.max_iterations:
            if (
                self.cfg.time_budget_sec
                and (time.time() - start) > self.cfg.time_budget_sec
            ):
                state["status"] = "time_budget_exhausted"
                break

            # 1) Planning step (concise research objective + plan)
            plan_prompt = (
                "You are an AI researcher. Propose a concise research objective and a 3-step plan "
                "with clear, testable milestones, focusing on a small but meaningful experiment. "
                "Return in 120 words."
            )
            plan = self._gen(plan_prompt, 1)[0]

            # 2) TTC: sample N candidate experiment designs and pick best
            ttc_out = ttc.budgeted_adaptive_deliberation(
                lambda p, n: self._gen(p, n),
                prompt=f"Refine this plan into a concrete experiment protocol with brief pseudo-code.\n{plan}",
                total_budget=self.cfg.samples_per_query,
                batch_size=max(1, self.cfg.samples_per_query // 2),
                scorer=self._score,
            )
            experiment = ttc_out["best"]

            # 3) Debate for sanity-check & verification hooks
            debate_out = debate.multi_agent_debate(
                lambda p, n: self._gen(p, n),
                topic_prompt=f"Is the following experiment well-posed and reproducible? Identify pitfalls and fixes.\n{experiment}",
                n_debaters=2,
                rounds=1,
            )
            reviewed = debate_out["consensus"]

            # 4) Reflection: critique and revise a draft methods section
            refl = reflection.critique_and_revise(
                lambda p, n: self._gen(p, n),
                draft=f"Methods draft (start from this experiment):\n{experiment}",
                passes=1,
            )
            methods = refl["final"]

            # 5) Update LaTeX and autosave
            with open(pm.draft_path, "r", encoding="utf-8") as f:
                tex = f.read()
            new_tex = tex.replace("TBD.", methods[:2000] + "\nTBD.")
            pm.autosave(new_tex)
            ok = pm.compile_pdf()
            pm.log(
                f"Iter {state['iter']}: plan, experiment, review added. "
                f"PDF compile {'succeeded' if ok else 'failed'}"
            )

            # 6) Save state
            state["iter"] += 1
            pm.save_state(state)

            # Human-in-the-loop prompt after each iter (if interactive)
            if self.cfg.interactive:
                print(
                    "\n[HUMAN LOOP] Press Enter to continue, or type a prompt to inject guidance. Type 'stop' to end."
                )
                try:
                    user = input().strip()
                except EOFError:
                    user = ""
                if user.lower() == "stop":
                    self.stop_flag = True
                elif user:
                    # feed guidance signal into next loop by appending to draft
                    with open(pm.draft_path, "a", encoding="utf-8") as f:
                        f.write("\n% HUMAN NOTE: " + user + "\n")
                    pm.autosave(open(pm.draft_path, "r", encoding="utf-8").read())
                    ok = pm.compile_pdf()
                    pm.log(
                        f"HITL note added. PDF compile {'succeeded' if ok else 'failed'}"
                    )
                if self.stop_flag:
                    state["status"] = "stopped_by_user"
                    break

        if state["status"] == "running":
            state["status"] = "complete_limit_reached"
            self.project.pm.save_state(state)
