"""
tests/test_all.py
=================
Unit test untuk semua fitur Automata Simulator.

Menguji:
    - Fitur 1: Simulasi DFA
    - Fitur 2: Regex → NFA (Thompson Construction)
    - Fitur 3: Minimasi DFA (Table-Filling)
    - Fitur 4: Ekuivalensi DFA

Cara menjalankan:
    python -m pytest tests/test_all.py -v
    # atau
    python tests/test_all.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dfa import DFA
from core.nfa import NFA, ThompsonConstruction, EPSILON
from utils.parser import parse_dfa_from_form


# ============================================================ #
#  HELPER UNTUK MEMBUAT DFA TEST                               #
# ============================================================ #

def make_dfa_ab_ends():
    """
    DFA yang menerima string atas {a,b} yang berakhir dengan 'ab'.
    Bahasa: {w | w berakhir dengan 'ab'}
    """
    return DFA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        start_state="q0",
        accept_states={"q2"},
        transitions={
            ("q0", "a"): "q1",
            ("q0", "b"): "q0",
            ("q1", "a"): "q1",
            ("q1", "b"): "q2",
            ("q2", "a"): "q1",
            ("q2", "b"): "q0",
        }
    )


def make_dfa_even_zeros():
    """
    DFA yang menerima string biner dengan jumlah '0' genap.
    Bahasa: {w ∈ {0,1}* | #0(w) adalah genap}
    """
    return DFA(
        states={"even", "odd"},
        alphabet={"0", "1"},
        start_state="even",
        accept_states={"even"},
        transitions={
            ("even", "0"): "odd",
            ("even", "1"): "even",
            ("odd", "0"): "even",
            ("odd", "1"): "odd",
        }
    )


def make_dfa_redundant():
    """
    DFA dengan state redundan (untuk test minimasi).
    Menerima string atas {0,1} dengan jumlah 0 genap.
    State q1 dan q3 ekuivalen, q0 dan q2 ekuivalen.
    """
    return DFA(
        states={"q0", "q1", "q2", "q3", "q4"},
        alphabet={"0", "1"},
        start_state="q0",
        accept_states={"q1", "q3"},
        transitions={
            ("q0", "0"): "q1",
            ("q0", "1"): "q2",
            ("q1", "0"): "q1",
            ("q1", "1"): "q1",
            ("q2", "0"): "q3",
            ("q2", "1"): "q4",
            ("q3", "0"): "q3",
            ("q3", "1"): "q3",
            ("q4", "0"): "q4",
            ("q4", "1"): "q4",
        }
    )


# ============================================================ #
#  FITUR 1: SIMULASI DFA                                       #
# ============================================================ #

def test_dfa_simulation():
    print("\n" + "="*55)
    print("  FITUR 1: SIMULASI DFA")
    print("="*55)

    dfa = make_dfa_ab_ends()

    test_cases = [
        ("ab",       True,  "Harus DITERIMA (berakhir 'ab')"),
        ("aab",      True,  "Harus DITERIMA (berakhir 'ab')"),
        ("bab",      True,  "Harus DITERIMA (berakhir 'ab')"),
        ("ba",       False, "Harus DITOLAK (tidak berakhir 'ab')"),
        ("",         False, "Harus DITOLAK (string kosong)"),
        ("ababab",   True,  "Harus DITERIMA (berakhir 'ab')"),
        ("abba",     False, "Harus DITOLAK"),
    ]

    all_pass = True
    for s, expected, desc in test_cases:
        result, steps = dfa.simulate(s)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result != expected:
            all_pass = False
        outcome = "DITERIMA" if result else "DITOLAK"
        print(f"  {status}  \"{s:10s}\"  →  {outcome:10s}  ({desc})")

    print(f"\n  Hasil: {'SEMUA LULUS ✅' if all_pass else 'ADA YANG GAGAL ❌'}")
    assert all_pass, "Test simulasi DFA gagal!"


def test_dfa_steps():
    """Pastikan log langkah simulasi benar."""
    dfa = make_dfa_ab_ends()
    accepted, steps = dfa.simulate("ab")

    assert accepted == True
    assert steps[0]["current_state"] == "q0"         # Mulai dari q0
    assert steps[1]["symbol"] == "a"                  # Baca 'a'
    assert steps[1]["next_state"] == "q1"             # Pindah ke q1
    assert steps[2]["symbol"] == "b"                  # Baca 'b'
    assert steps[2]["next_state"] == "q2"             # Pindah ke q2
    print("\n  ✅ PASS  Log langkah simulasi benar")


# ============================================================ #
#  FITUR 2: REGEX → NFA                                        #
# ============================================================ #

def test_thompson_construction():
    print("\n" + "="*55)
    print("  FITUR 2: REGEX → NFA (Thompson Construction)")
    print("="*55)

    tc = ThompsonConstruction()

    test_cases = [
        # (regex, string, expected, deskripsi)
        ("a",        "a",    True,  "literal 'a' menerima 'a'"),
        ("a",        "b",    False, "literal 'a' menolak 'b'"),
        ("a|b",      "a",    True,  "union: 'a' diterima"),
        ("a|b",      "b",    True,  "union: 'b' diterima"),
        ("a|b",      "c",    False, "union: 'c' ditolak"),
        ("ab",       "ab",   True,  "concat: 'ab' diterima"),
        ("ab",       "a",    False, "concat: 'a' saja ditolak"),
        ("a*",       "",     True,  "star: string kosong diterima"),
        ("a*",       "aaa",  True,  "star: 'aaa' diterima"),
        ("a*",       "b",    False, "star: 'b' ditolak"),
        ("a+",       "",     False, "plus: string kosong ditolak"),
        ("a+",       "a",    True,  "plus: 'a' diterima"),
        ("a+",       "aaa",  True,  "plus: 'aaa' diterima"),
        ("a?",       "",     True,  "question: string kosong diterima"),
        ("a?",       "a",    True,  "question: 'a' diterima"),
        ("a?",       "aa",   False, "question: 'aa' ditolak"),
        ("(a|b)*",   "abba", True,  "complex: 'abba' diterima"),
        ("(a|b)*",   "ccc",  False, "complex: 'ccc' ditolak"),
        ("a(b|c)*",  "abc",  True,  "complex: 'abc' diterima"),
        ("a(b|c)*",  "acc",  True,  "complex: 'acc' diterima"),
        ("a(b|c)*",  "",     False, "complex: kosong ditolak"),
    ]

    all_pass = True
    for regex, string, expected, desc in test_cases:
        try:
            nfa = tc.regex_to_nfa(regex)
            result, _ = nfa.simulate(string)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            if result != expected:
                all_pass = False
            print(f"  {status}  regex={regex:12s}  str={string!r:8s}  → {'OK' if result==expected else 'SALAH'}  ({desc})")
        except Exception as e:
            print(f"  ❌ ERROR  regex={regex}  ({e})")
            all_pass = False

    print(f"\n  Hasil: {'SEMUA LULUS ✅' if all_pass else 'ADA YANG GAGAL ❌'}")
    assert all_pass, "Test Thompson Construction gagal!"


# ============================================================ #
#  FITUR 3: MINIMASI DFA                                       #
# ============================================================ #

def test_dfa_minimization():
    print("\n" + "="*55)
    print("  FITUR 3: MINIMASI DFA")
    print("="*55)

    dfa = make_dfa_redundant()
    print(f"\n  DFA asli: {len(dfa.states)} state")

    min_dfa, state_mapping, merged_groups = dfa.minimize()
    print(f"  DFA minimal: {len(min_dfa.states)} state")

    # Verifikasi minimasi mengurangi jumlah state
    assert len(min_dfa.states) < len(dfa.states), "Minimasi harus mengurangi jumlah state!"

    # Verifikasi DFA minimal menerima bahasa yang sama
    test_strings = ["0", "1", "00", "01", "10", "11", "000", "010"]
    lang_preserved = True
    for s in test_strings:
        r1, _ = dfa.simulate(s)
        r2, _ = min_dfa.simulate(s)
        if r1 != r2:
            print(f"  ❌ Bahasa tidak preserved untuk '{s}': DFA={r1}, MinDFA={r2}")
            lang_preserved = False

    assert lang_preserved, "Minimasi harus mempertahankan bahasa yang diterima!"

    print(f"  State mapping: {state_mapping}")
    print(f"  Grup yang digabungkan:")
    for g in merged_groups:
        if len(g) > 1:
            print(f"    {sorted(g)} → satu state")

    print(f"\n  ✅ PASS  Minimasi berhasil: {len(dfa.states)} → {len(min_dfa.states)} state")
    print(f"  ✅ PASS  Bahasa tetap sama setelah minimasi")


# ============================================================ #
#  FITUR 4: EKUIVALENSI DFA                                    #
# ============================================================ #

def test_dfa_equivalence():
    print("\n" + "="*55)
    print("  FITUR 4: CEK EKUIVALENSI DFA")
    print("="*55)

    # Test 1: DFA dan versinya yang terminimasi harus ekuivalen
    dfa = make_dfa_redundant()
    min_dfa, _, _ = dfa.minimize()

    is_eq, counterexample = dfa.is_equivalent_to(min_dfa)
    print(f"\n  Test 1: DFA vs DFA Minimal")
    print(f"    Ekuivalen: {is_eq}")
    assert is_eq, "DFA dan versi minimalnya harus ekuivalen!"
    print(f"  ✅ PASS")

    # Test 2: Dua DFA berbeda yang menerima bahasa yang sama
    dfa_a = make_dfa_even_zeros()
    # Buat DFA lain yang juga menerima jumlah 0 genap (tapi dengan state berbeda)
    dfa_b = DFA(
        states={"s0", "s1"},
        alphabet={"0", "1"},
        start_state="s0",
        accept_states={"s0"},
        transitions={
            ("s0", "0"): "s1",
            ("s0", "1"): "s0",
            ("s1", "0"): "s0",
            ("s1", "1"): "s1",
        }
    )
    is_eq2, _ = dfa_a.is_equivalent_to(dfa_b)
    print(f"\n  Test 2: Dua DFA untuk 'jumlah 0 genap'")
    print(f"    Ekuivalen: {is_eq2}")
    assert is_eq2, "Kedua DFA harus ekuivalen!"
    print(f"  ✅ PASS")

    # Test 3: Dua DFA yang TIDAK ekuivalen
    dfa_c = make_dfa_ab_ends()  # Menerima string berakhir 'ab'
    dfa_d = make_dfa_even_zeros()  # Menerima jumlah 0 genap
    is_eq3, ce = dfa_c.is_equivalent_to(dfa_d)
    print(f"\n  Test 3: DFA berbeda bahasa (harus tidak ekuivalen)")
    print(f"    Ekuivalen: {is_eq3}")
    print(f"    Counterexample: '{ce}'")
    assert not is_eq3, "DFA berbeda bahasa harus tidak ekuivalen!"
    print(f"  ✅ PASS")


# ============================================================ #
#  TEST PARSER                                                  #
# ============================================================ #

def test_parser():
    print("\n" + "="*55)
    print("  FITUR PARSER & VALIDASI INPUT")
    print("="*55)

    # Test parse yang valid
    dfa, err = parse_dfa_from_form(
        "q0,q1,q2",
        "a,b",
        "q0",
        "q2",
        "q0,a,q1\nq1,b,q2"
    )
    assert dfa is not None and err is None, f"Parse valid gagal: {err}"
    print("  ✅ PASS  Parse DFA valid")

    # Test error: state awal tidak ada
    dfa, err = parse_dfa_from_form("q0,q1", "a", "qX", "q1", "q0,a,q1")
    assert dfa is None and err is not None
    print("  ✅ PASS  Error: state awal tidak valid")

    # Test error: simbol tidak di alphabet
    dfa, err = parse_dfa_from_form("q0,q1", "a", "q0", "q1", "q0,b,q1")
    assert dfa is None and err is not None
    print("  ✅ PASS  Error: simbol tidak di alphabet")

    # Test error: format transisi salah
    dfa, err = parse_dfa_from_form("q0,q1", "a", "q0", "q1", "q0 a q1")
    assert dfa is None and err is not None
    print("  ✅ PASS  Error: format transisi salah")


# ============================================================ #
#  MAIN RUNNER                                                  #
# ============================================================ #

def run_all_tests():
    print("\n" + "★"*55)
    print("  AUTOMATA SIMULATOR – UNIT TESTING")
    print("★"*55)

    tests = [
        ("Simulasi DFA",           test_dfa_simulation),
        ("Log Langkah DFA",        test_dfa_steps),
        ("Thompson Construction",  test_thompson_construction),
        ("Minimasi DFA",           test_dfa_minimization),
        ("Ekuivalensi DFA",        test_dfa_equivalence),
        ("Parser & Validasi",      test_parser),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"\n  ❌ GAGAL: {name} – {e}")
            failed += 1
        except Exception as e:
            print(f"\n  ❌ ERROR: {name} – {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "★"*55)
    print(f"  HASIL AKHIR: {passed}/{len(tests)} test lulus")
    if failed == 0:
        print("  ✅ SEMUA TEST BERHASIL!")
    else:
        print(f"  ❌ {failed} test GAGAL.")
    print("★"*55)
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
