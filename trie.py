__author__ = "Elad Nachmias"
__email__ = "eladnah@gmail.com"
__date__ = "2020-08-01"

import functools
import dataclasses
from typing import TypeVar, Generic, List, Tuple, Dict, Iterator


__all__ = ['TrieNode']


SequenceElementType = TypeVar('SequenceElementType')
SequenceType = Tuple[SequenceElementType, ...]


@dataclasses.dataclass
class TrieEdge:
    element: SequenceElementType
    sub_sequence: SequenceType
    child: 'TrieNode'


def find_common_prefix_length(seq1: SequenceType, seq2: SequenceType):
    common_prefix_length = 0
    for element1, element2 in zip(seq1, seq2):
        if element1 != element2:
            break
        common_prefix_length += 1
    return common_prefix_length


class TrieNode(Generic[SequenceElementType]):
    def __init__(self, create_from_sequences: List[SequenceType], is_terminal: bool = False):
        assert all(isinstance(seq, tuple) for seq in create_from_sequences)
        self.out_edges: Dict[SequenceElementType, TrieEdge] = {}
        self.is_terminal = bool(is_terminal)
        self.nr_sequences = int(self.is_terminal)
        for sequence in create_from_sequences:
            self.add_sequence(sequence)

    def __len__(self):
        return self.nr_sequences

    def add_sequence(self, sequence: SequenceType):
        if len(sequence) == 0:
            if not self.is_terminal:
                self.is_terminal = True
                self.nr_sequences += 1
            return
        first_element, remained_suffix = sequence[0], sequence[1:]
        if first_element in self.out_edges:
            out_edge = self.out_edges[first_element]
            assert out_edge.element == first_element
            if out_edge.sub_sequence == remained_suffix[:len(out_edge.sub_sequence)]:
                out_edge.child.add_sequence(remained_suffix[len(out_edge.sub_sequence):])
            else:
                old_out_edge = out_edge
                assert len(old_out_edge.sub_sequence) >= 1
                common_prefix_length = find_common_prefix_length(old_out_edge.sub_sequence, remained_suffix)
                assert 0 <= common_prefix_length < len(old_out_edge.sub_sequence)
                new_immediate_out_edge = TrieEdge(
                    element=first_element,
                    sub_sequence=old_out_edge.sub_sequence[:common_prefix_length],
                    child=TrieNode(create_from_sequences=[]))
                self.out_edges[first_element] = new_immediate_out_edge
                new_immediate_out_edge.child._add_subtree_under_non_exist_prefix(
                    sub_tree=old_out_edge.child, prefix=old_out_edge.sub_sequence[common_prefix_length:])
                new_immediate_out_edge.child.add_sequence(remained_suffix[common_prefix_length:])
        else:
            self.out_edges[first_element] = TrieEdge(
                element=first_element, sub_sequence=remained_suffix,
                child=TrieNode(create_from_sequences=[], is_terminal=True))
        self.nr_sequences = int(self.is_terminal) + sum(edge.child.nr_sequences for edge in self.out_edges.values())

    def _add_subtree_under_non_exist_prefix(self, sub_tree: 'TrieNode', prefix: SequenceType):
        assert len(prefix) > 0
        assert prefix[0] not in self.out_edges
        self.out_edges[prefix[0]] = TrieEdge(element=prefix[0], sub_sequence=prefix[1:], child=sub_tree)
        self.nr_sequences = int(self.is_terminal) + sum(edge.child.nr_sequences for edge in self.out_edges.values())

    def __contains__(self, sequence: SequenceType) -> bool:
        remained_suffix = tuple(sequence)
        cur_trie_node = self
        while True:
            if len(remained_suffix) == 0:
                return cur_trie_node.is_terminal
            first_remained_element, remained_suffix = remained_suffix[0], remained_suffix[1:]
            if first_remained_element not in cur_trie_node.out_edges:
                return False
            out_edge = cur_trie_node.out_edges[first_remained_element]
            assert out_edge.element == first_remained_element
            if out_edge.sub_sequence != remained_suffix[:len(out_edge.sub_sequence)]:
                return False
            remained_suffix = remained_suffix[len(out_edge.sub_sequence):]
            cur_trie_node = out_edge.child

    def iter_sequence_edges(self, sequence: SequenceType) -> Iterator[TrieEdge]:
        if sequence not in self:
            raise ValueError(f'Given sequence `{sequence}` is not contained in this trie.')
        remained_suffix = tuple(sequence)
        cur_trie_node = self
        while True:
            if len(remained_suffix) == 0:
                assert cur_trie_node.is_terminal
                return
            first_remained_element, remained_suffix = remained_suffix[0], remained_suffix[1:]
            assert first_remained_element in cur_trie_node.out_edges
            out_edge = cur_trie_node.out_edges[first_remained_element]
            assert out_edge.element == first_remained_element
            assert out_edge.sub_sequence == remained_suffix[:len(out_edge.sub_sequence)]
            remained_suffix = remained_suffix[len(out_edge.sub_sequence):]
            cur_trie_node = out_edge.child
            yield out_edge

    def __iter__(self) -> Iterator[SequenceType]:
        if self.is_terminal:
            yield ()
        for first_element, out_edge in self.out_edges.items():
            for suffix in out_edge.child:
                yield (first_element,) + out_edge.sub_sequence + suffix

    def get_sequence_shortest_unique_prefix(self, sequence: SequenceType):
        edges = list(self.iter_sequence_edges(sequence))
        if len(self) == 1:
            return ()
        return functools.reduce(
            tuple.__add__,
            ((edge.element,) + (edge.sub_sequence if edge_nr < len(edges) or len(edge.child.out_edges) > 0 else ())
             for edge_nr, edge in enumerate(edges, 1)),
            ())
