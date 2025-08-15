from __future__ import annotations

from typing import Any, Callable, Dict, List

DEBATE_SYS = "You are debating to arrive at a correct, clear, and verifiable solution. Be concise."


def multi_agent_debate(
    provider_generate: Callable[[str, int], List[str]],
    topic_prompt: str,
    n_debaters: int = 2,
    rounds: int = 2,
) -> Dict[str, Any]:
    stances = [f"Debater {i+1}" for i in range(n_debaters)]
    transcripts: List[str] = []
    current = topic_prompt
    for r in range(rounds):
        round_utterances: List[str] = []
        for s in stances:
            p = f"{DEBATE_SYS}\nTopic: {topic_prompt}\n{ s }: Provide your argument for this round {r+1}."
            out = provider_generate(p, 1)[0]
            round_utterances.append(f"{s}: {out}")
        transcripts.extend(round_utterances)
        # consensus step
        consensus_prompt = (
            f"{DEBATE_SYS}\nGiven the following arguments, synthesize a consensus that is likely correct, "
            "with explicit verification steps if possible.\n"
            + "\n".join(round_utterances)
        )
        current = provider_generate(consensus_prompt, 1)[0]
    return {"consensus": current, "transcript": transcripts}
