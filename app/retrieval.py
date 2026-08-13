"""Retrieval over the contents of data/. Deliberately empty.

The baseline handler does not read data/ at all. It answers from the
model's own knowledge, which is why it scores what it scores.

Everything the gold set asks about is somewhere in data/, but the files
disagree with each other, use inconsistent district spellings, mix units,
and in a couple of cases say nothing at all about a district that the
calendar claims exists. Deciding what to trust is the exercise.

Some directions, none of them mandatory:

  - Keyword or BM25 lookup is often enough at this corpus size. Embeddings
    are not obviously worth the latency budget, but measure rather than
    assume.
  - District names need normalizing before anything else works. The KCC
    extract, the calendar, and the FAQ dump do not spell them the same way.
  - Doses carry units. A number without its unit is worse than no answer.
  - When two files disagree, something has to break the tie: recency,
    source type, or declining to answer.
  - Returning nothing is a valid retrieval result and the handler should be
    able to act on it.
"""
