import os

from sciresearch_ai.paper.manager import PaperManager


def test_validate_citations(tmp_path):
    pm = PaperManager(str(tmp_path))
    draft = tmp_path / "paper" / "draft.tex"
    bib = tmp_path / "paper" / "refs.bib"
    # valid citation
    draft.write_text("Some text \cite{valid}.", encoding="utf-8")
    bib.write_text("@article{valid, title={X}}", encoding="utf-8")
    assert pm.validate_citations()
    # missing citation
    draft.write_text("Reference \cite{missing}.", encoding="utf-8")
    assert not pm.validate_citations()


def test_check_innovation(tmp_path):
    pm = PaperManager(str(tmp_path))
    draft = tmp_path / "paper" / "draft.tex"
    draft.write_text("This work presents a novel approach.", encoding="utf-8")
    assert pm.check_innovation()
    draft.write_text("This work has no claims.", encoding="utf-8")
    assert not pm.check_innovation()


def test_validate_paper(monkeypatch, tmp_path):
    pm = PaperManager(str(tmp_path))
    draft = tmp_path / "paper" / "draft.tex"
    bib = tmp_path / "paper" / "refs.bib"
    draft.write_text("An innovative idea \cite{ok}.", encoding="utf-8")
    bib.write_text("@article{ok, title={Y}}", encoding="utf-8")
    # avoid running pdflatex
    monkeypatch.setattr(PaperManager, "compile_pdf", lambda self: True)
    assert pm.validate_paper()
