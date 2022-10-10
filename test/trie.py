__author__ = "Elad Nachmias"
__email__ = "eladnah@gmail.com"
__date__ = "2020-08-01"

from itertools import permutations

from trie import TrieNode


def test_trie():
    sequences_combinations = [
        [],
        [()],
        [('a',)],
        [('a',), ('a',)],
        [('a',), ()],
        [('a',), ('b',)],
        [('a',), ('a', 'a')],
        [('a',), ('a', 'b')],
        [('a',), ('b', 'a')],
        [('a',), ('a', 'a', 'a')],
        [('a',), ('a', 'a', 'b')],
        [('a',), ('a', 'a', 'b'), ('b',)],
        [('a',), ('a', 'a', 'b'), ('a', 'b'), ('b',)],
        [('a',), ('a', 'a', 'b'), ('a', 'a'), ('b',)],
        [('a',), ('b', 'b'), ('b',), ('c',), ('c', 'c')],
        [('a', 'b', 'c', 'd'), ('a',)],
        [('a', 'b', 'c', 'd'), ('a', 'b')],
        [('a', 'b', 'c', 'd'), ('a', 'b', 'c')],
        [('a', 'b', 'c', 'd'), ('a', 'b', 'c', 'd')],
    ]
    all_checked_sequences = set(
        seq for sequences_combination in sequences_combinations for seq in sequences_combination)
    for sequences_combination in sequences_combinations:
        for sequences_permutation in permutations(sequences_combination):
            sequences_combination_set = set(sequences_combination)
            trie = TrieNode(sequences_permutation)
            try:
                all_sequences_in_generated_trie = set(trie)
            except Exception as e:
                raise RuntimeError(
                    f'Test failed: got exception {type(e)} while creating a Trie from `{sequences_permutation}`. '
                    f'Exception: {e}.')
            if all_sequences_in_generated_trie != sequences_combination_set:
                raise RuntimeError(
                    f'Test failed: when inserting `{sequences_permutation}` (in this order) we get '
                    f'`{all_sequences_in_generated_trie}`.')
            for non_exists_seq in all_checked_sequences - sequences_combination_set:
                if non_exists_seq in trie:
                    raise RuntimeError(
                        f'Test failed: Trie.__contains__({non_exists_seq}) returned True '
                        f'for Trie built from `{sequences_permutation}`.')
            if len(trie) != len(sequences_combination_set):
                raise RuntimeError(
                    f'Test failed: len(Trie) [{len(trie)}] != '
                    f'len(sequences_combination_set) [{len(sequences_combination_set)}].')
            for seq in sequences_combination:
                if seq not in trie:
                    raise RuntimeError(
                        f'Test failed: Trie.__contains__({seq}) returned False '
                        f'for Trie built from `{sequences_permutation}`.')
                if len(seq) > 0:
                    additional_should_not_exist_seqs = \
                        {seq + (seq[-1],), (seq[0],) + seq, (seq[0],) + seq + (seq[-1],),
                         (seq[0],), (seq[-1],), seq[:-1], seq[1:]} - sequences_combination_set
                    for should_not_exist_seq in additional_should_not_exist_seqs:
                        if should_not_exist_seq in trie:
                            raise RuntimeError(
                                f'Test failed: Trie.__contains__({should_not_exist_seq}) returned True '
                                f'for Trie built from `{sequences_permutation}`.')
                try:
                    sequence_edges = list(trie.iter_sequence_edges(seq))
                except Exception as e:
                    raise RuntimeError(
                        f'Test failed: Got `{e.__class__.__name__}` exception while running '
                        f'`iter_sequence_edges()` for Trie built from {sequences_permutation}. Exception: {e}.')
                seq_rebuilt_from_iter_sequence_edges = functools.reduce(
                    tuple.__add__, ((edge.element,) + edge.sub_sequence for edge in sequence_edges), ())
                if seq != seq_rebuilt_from_iter_sequence_edges:
                    raise RuntimeError(
                        f'Test failed: For Trie received by inserting `{sequences_permutation}`, when iterating '
                        f'over edges of sequence `{seq}` we get `{seq_rebuilt_from_iter_sequence_edges}` '
                        f'and edges: `{sequence_edges}`.')
    common_prefix_test_data = [
        ([()], [()]),
        ([(1,)], [()]),
        ([(1,), (1,)], [(), ()]),
        ([(1, 1)], [()]),
        ([(1, 2)], [()]),
        ([(1, 2, 3, 4)], [()]),
        ([(1,), (2,)], [(1,), (2,)]),
        ([(1,), (1, 2,)], [(1,), (1, 2)]),
        ([(1, 9), (2, 9)], [(1,), (2,)]),
        ([(1, 8, 9), (2, 8, 9)], [(1,), (2,)]),
        ([(1, 8, 9), (2, 8, 8)], [(1,), (2,)]),
        ([(1, 8, 9), (2, 6, 7)], [(1,), (2,)]),
        ([(1, 9), (2, 8)], [(1,), (2,)]),
        ([(1, 5, 6, 7), (2, 5, 6, 7)], [(1,), (2,)]),
        ([(1, 2, 3, 1), (1, 2, 3, 1, 7)], [(1, 2, 3, 1), (1, 2, 3, 1, 7)]),
        ([(1, 2, 3, 1, 9, 9), (1, 2, 3, 1, 7, 7)], [(1, 2, 3, 1, 9), (1, 2, 3, 1, 7)]),
        ([(1, 2, 3, 1), (1, 2, 3, 1, 7), (1, 2, 3, 1, 8)], [(1, 2, 3, 1), (1, 2, 3, 1, 7), (1, 2, 3, 1, 8)]),
        ([(1, 1, 5, 6, 7), (1, 2, 5, 6, 7)], [(1, 1), (1, 2)]),
        ([(1, 1, 6, 6, 7), (1, 2, 5, 6, 7)], [(1, 1), (1, 2)]),
        ([(1, 1, 6, 6, 7), (1, 2, 5, 6, 7), (1,)], [(1, 1), (1, 2), (1,)])
    ]
    for input_seqs, expected_unique_prefixes in common_prefix_test_data:
        trie = TrieNode(input_seqs)
        ret_shortest_prefixes = [trie.get_sequence_shortest_unique_prefix(seq) for seq in input_seqs]
        if ret_shortest_prefixes != expected_unique_prefixes:
            raise RuntimeError(
                f'Test failed: Trie generated from sequences `{input_seqs}` returned `{ret_shortest_prefixes}` '
                f'for `Trie.get_sequence_shortest_unique_prefix()` while expected `{expected_unique_prefixes}`.')
