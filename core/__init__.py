"""
core/__init__.py
Paket inti berisi implementasi DFA dan NFA.
"""
from .dfa import DFA
from .nfa import NFA, ThompsonConstruction, EPSILON, test_regex_direct

__all__ = ["DFA", "NFA", "ThompsonConstruction", "EPSILON", "test_regex_direct"]
