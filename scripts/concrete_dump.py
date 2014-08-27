#!/usr/bin/env python

"""Print human-readable information about a Communication to stdout

concrete_dump.py is a command-line script for printing out information
about a Concrete Communication.
"""

import argparse
from collections import defaultdict
from operator import attrgetter

import concrete.util


def main():
    parser = argparse.ArgumentParser(description="Print information about a Concrete Communication to stdout")
    parser.add_argument("--char-offsets", help="Print token text extracted from character offsets "
                        "(not the text stored in the tokenization) in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--dependency", help="Print HEAD tags for first dependency parse in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--lemmas", help="Print lemma token tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--mentions", help="Print whitespace-separated tokens, with entity mentions wrapped "
                        "using <ENTITY ID=x> tags, where 'x' is the (zero-indexed) entity number",
                        action="store_true")
    parser.add_argument("--ner", help="Print Named Entity Recognition token tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--pos", help="Print Part-Of-Speech token tags in 'ConLL-style' format",
                        action="store_true")
    parser.add_argument("--tokens", help="Print whitespace-seperated tokens for *all* Tokenizations in a "
                        "Communication.  Each sentence tokenization is printed on a separate line, and "
                        "empty lines indicate a section break",
                        action="store_true")
    parser.add_argument("--treebank", help="Print Penn-Treebank style parse trees for *all* Constituent "
                        "Parses in the Communication",
                        action="store_true")
    parser.add_argument("communication_file")
    args = parser.parse_args()

    comm = concrete.util.read_communication_from_file(args.communication_file)

    if args.char_offsets or args.dependency or args.lemmas or args.ner or args.pos:
        print_conll_style_tags_for_communication(
            comm, char_offsets=args.char_offsets, dependency=args.dependency, lemmas=args.lemmas, ner=args.ner, pos=args.pos)
    elif args.mentions:
        print_tokens_with_entityMentions(comm)
    elif args.tokens:
        print_tokens_for_communication(comm)
    elif args.treebank:
        print_penn_treebank_for_communication(comm)


def print_conll_style_tags_for_communication(comm, char_offsets=False, dependency=False, lemmas=False, ner=False, pos=False):
    """Print 'ConLL-style' tags for the tokens in a Communication

    Args:
        comm: A Concrete Communication object
        char_offsets: A boolean flag for printing token text specified by
            a Token's (optional) TextSpan
        dependency: A boolean flag for printing dependency parse HEAD tags
        lemmas: A boolean flag for printing lemma tags
        ner: A boolean flag for printing Named Entity Recognition tags
        pos: A boolean flag for printing Part-of-Speech tags
    """
    header_fields = ["INDEX", "TOKEN"]
    if char_offsets:
        header_fields.append("CHAR")
    if lemmas:
        header_fields.append("LEMMA")
    if pos:
        header_fields.append("POS")
    if ner:
        header_fields.append("NER")
    if dependency:
        header_fields.append("HEAD")
    print "\t".join(header_fields)
    dashes = ["-"*len(fieldname) for fieldname in header_fields]
    print "\t".join(dashes)

    for tokenization in get_tokenizations(comm):
        token_taggings = []

        if char_offsets:
            token_taggings.append(get_char_offset_tags_for_tokenization(comm, tokenization))
        if lemmas:
            token_taggings.append(get_lemma_tags_for_tokenization(tokenization))
        if pos:
            token_taggings.append(get_pos_tags_for_tokenization(tokenization))
        if ner:
            token_taggings.append(get_ner_tags_for_tokenization(tokenization))
        if dependency:
            token_taggings.append(get_conll_head_tags_for_tokenization(tokenization))
        print_conll_style_tags_for_tokenization(tokenization, token_taggings)
        print


def print_conll_style_tags_for_tokenization(tokenization, token_taggings):
    """Print 'ConLL-style' tags for the tokens in a tokenization

    Args:
        tokenization: A Concrete Tokenization object
        token_taggings: A list of lists of token tag strings
    """
    if tokenization.tokenList:
        for i, token in enumerate(tokenization.tokenList.tokens):
            token_tags = [str(token_tagging[i]) for token_tagging in token_taggings]
            fields = [str(i+1), token.text]
            fields.extend(token_tags)
            print "\t".join(fields)


def print_tokens_with_entityMentions(comm):
    entityMentions_by_tokenizationId = get_entityMentions_by_tokenizationId(comm)
    entity_number_for_entityMention_uuid = get_entity_number_for_entityMention_uuid(comm)
    tokenizations_by_section = get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text for token in tokenization.tokenList.tokens]
                if tokenization.uuid.uuidString in entityMentions_by_tokenizationId:
                    for entityMention in entityMentions_by_tokenizationId[tokenization.uuid.uuidString]:
                        # TODO: Handle non-contiguous tokens in a tokenIndexLists
                        first_token_index = entityMention.tokens.tokenIndexList[0]
                        last_token_index = entityMention.tokens.tokenIndexList[-1]
                        entity_number = entity_number_for_entityMention_uuid[entityMention.uuid.uuidString]
                        text_tokens[first_token_index] = "<ENTITY ID=%d>%s" % (entity_number, text_tokens[first_token_index])
                        text_tokens[last_token_index] = "%s</ENTITY>" % text_tokens[last_token_index]
                print " ".join(text_tokens)
        print


def print_tokens_for_communication(comm):
    """
    """
    tokenizations_by_section = get_tokenizations_grouped_by_section(comm)

    for tokenizations_in_section in tokenizations_by_section:
        for tokenization in tokenizations_in_section:
            if tokenization.tokenList:
                text_tokens = [token.text for token in tokenization.tokenList.tokens]
                print " ".join(text_tokens)
        print


def print_penn_treebank_for_communication(comm):
    """Print Penn-Treebank parse trees for all tokenizations

    Args:
        comm: A Concrete Communication object
    """
    tokenizations = get_tokenizations(comm)

    for tokenization in tokenizations:
        if tokenization.parse:
            print penn_treebank_for_parse(tokenization.parse) + "\n\n"


def penn_treebank_for_parse(parse):
    """Get a Penn-Treebank style string for a Concrete Parse object

    Args:
        parse: A Concrete Parse object

    Returns:
        A string containing a Penn Treebank style parse tree representation
    """
    def _traverse_parse(nodes, node_index, indent=0):
        s = ""
        indent += len(nodes[node_index].tag) + 2
        if nodes[node_index].childList:
            s += "(%s " % nodes[node_index].tag
            for i, child_node_index in enumerate(nodes[node_index].childList):
                if i > 0:
                    s += "\n" + " "*indent
                s += _traverse_parse(nodes, child_node_index, indent)
            s += ")"
        else:
            s += nodes[node_index].tag
        return s

    sorted_nodes = sorted(parse.constituentList, key=attrgetter('id'))
    return _traverse_parse(sorted_nodes, 0)


def get_char_offset_tags_for_tokenization(comm, tokenization):
    """TODOC:
    """
    if tokenization.tokenList:
        char_offset_tags = [None]*len(tokenization.tokenList.tokens)

        if comm.text:
            for i, token in enumerate(tokenization.tokenList.tokens):
                if token.textSpan:
                    char_offset_tags[i] = comm.text[token.textSpan.start:token.textSpan.ending]
        return char_offset_tags


def get_conll_head_tags_for_tokenization(tokenization, dependency_parse_index=0):
    """Get a list of ConLL 'HEAD tags' for a tokenization

    In the ConLL data format:

        http://ufal.mff.cuni.cz/conll2009-st/task-description.html

    the HEAD for a token is the (1-indexed) index of that token's
    parent token.  The root token of the dependency parse has a HEAD
    index of 0.

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of ConLL 'HEAD tag' strings, with one HEAD tag for each
        token in the supplied tokenization.  If a token does not have
        a HEAD tag (e.g. punctuation tokens), the HEAD tag is an empty
        string.

        If the tokenization does not have a Dependency Parse, this
        function returns a list of empty strings for each token in the
        supplied tokenization.
    """
    if tokenization.tokenList:
        # Tokens that are not part of the dependency parse
        # (e.g. punctuation) are represented using an empty string
        head_list = [""]*len(tokenization.tokenList.tokens)

        if tokenization.dependencyParseList:
            for dependency in tokenization.dependencyParseList[dependency_parse_index].dependencyList:
                if dependency.gov is None:
                    head_list[dependency.dep] = 0
                else:
                    head_list[dependency.dep] = dependency.gov + 1
        return head_list
    else:
        return []


def get_entityMentions_by_tokenizationId(comm):
    """Get entity mentions for a Communication grouped by Tokenization UUID string

    Args:
        comm: A Concrete Communication object

    Returns:
        A dictionary of lists of EntityMentions, where the dictionary
        keys are Tokenization UUID strings.
    """
    mentions_by_tokenizationId = defaultdict(list)
    if comm.entitySets:
        for entitySet in comm.entitySets:
            for entity in entitySet.entityList:
                for entityMention in entity.mentionList:
                    mentions_by_tokenizationId[entityMention.tokens.tokenizationId.uuidString].append(entityMention)
    return mentions_by_tokenizationId


def get_entity_number_for_entityMention_uuid(comm):
    """Create mapping from EntityMention UUID to (zero-indexed) 'Entity Number'

    Args:
        comm: A Concrete Communication object

    Returns:
        A dictionary where the keys are EntityMention UUID strings,
        and the values are "Entity Numbers", where the first Entity is
        assigned number 0, the second Entity is assigned number 1,
        etc.
    """
    entity_number_for_entityMention_uuid = {}
    entity_number_counter = 0

    if comm.entitySets:
        for entitySet in comm.entitySets:
            for entity in entitySet.entityList:
                for entityMention in entity.mentionList:
                    entity_number_for_entityMention_uuid[entityMention.uuid.uuidString] = entity_number_counter
                entity_number_counter += 1
    return entity_number_for_entityMention_uuid


def get_lemma_tags_for_tokenization(tokenization):
    """Get lemma tags for a tokenization

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of lemma tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        lemma_tags = [""]*len(tokenization.tokenList.tokens)
        if tokenization.lemmaList:
            tag_for_tokenIndex = {}
            for taggedToken in tokenization.lemmaList.taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokens):
                if i in tag_for_tokenIndex:
                    lemma_tags[i] = tag_for_tokenIndex[i]
        return lemma_tags


def get_ner_tags_for_tokenization(tokenization):
    """Get Named Entity Recognition tags for a tokenization

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of NER tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        ner_tags = [""]*len(tokenization.tokenList.tokens)
        if tokenization.nerTagList:
            tag_for_tokenIndex = {}
            for taggedToken in tokenization.nerTagList.taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokens):
                try:
                    ner_tags[i] = tag_for_tokenIndex[i]
                except IndexError:
                    ner_tags[i] = ""
                if ner_tags[i] == "NONE":
                    ner_tags[i] = ""
        return ner_tags


def get_pos_tags_for_tokenization(tokenization):
    """Get Part-of-Speech tags for a tokenization

    Args:
        tokenization: A Concrete Tokenization object

    Returns:
        A list of POS tags for each token in the Tokenization
    """
    if tokenization.tokenList:
        pos_tags = [""]*len(tokenization.tokenList.tokens)
        if tokenization.posTagList:
            tag_for_tokenIndex = {}
            for taggedToken in tokenization.posTagList.taggedTokenList:
                tag_for_tokenIndex[taggedToken.tokenIndex] = taggedToken.tag
            for i, token in enumerate(tokenization.tokenList.tokens):
                if i in tag_for_tokenIndex:
                    pos_tags[i] = tag_for_tokenIndex[i]
        return pos_tags


def get_tokenizations(comm):
    """Returns a flat list of all Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        A list of all Tokenization objects within the Communication
    """
    tokenizations = []

    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenizations.append(tokenization)
    return tokenizations


def get_tokenizations_grouped_by_section(comm):
    """Returns a list of lists of Tokenization objects in a Communication

    Args:
        comm: A Concrete Communication

    Returns:
        Returns a list of lists of Tokenization objects, where the
        Tokenization objects are grouped by Section
    """
    tokenizations_by_section = []

    if comm.sectionSegmentations:
        for sectionSegmentation in comm.sectionSegmentations:
            for section in sectionSegmentation.sectionList:
                tokenizations_in_section = []
                if section.sentenceSegmentation:
                    for sentenceSegmentation in section.sentenceSegmentation:
                        for sentence in sentenceSegmentation.sentenceList:
                            for tokenization in sentence.tokenizationList:
                                tokenizations_in_section.append(tokenization)
                tokenizations_by_section.append(tokenizations_in_section)

    return tokenizations_by_section


if __name__ == "__main__":
    main()
