---
date: 12 July 2023
status: draft proposal v0.1
author: Benjamin Bollen
copyright: © 2023. This work is licensed under a [CC0 license](https://creativecommons.org/publicdomain/zero/1.0/legalcode).
---

# Building structured world models from unstructured data

## Motivation

In this specification draft we outline an algorithm to construct
a structured representation of an unstructured body of text,
leveraging a large language model (LLM).

The objectives of building a structured representation is to obtain 
an operational, intermediate representation. Operational is understood
to have two aspects: reliability and performance.
The representation is intermediate as we focus in this work on leveraging
LLMs for their ability to extract semantic meaning from texts 
better than previous techniques (and in broad domains without pretraining).

It is therefore assumed that the resulting structure can be further queried
or operated on for the intended application - this can again be an LLM
to synthesize responses from structured retrievals, but need not be limited to that.

An ability to quantify the degree of correctness of the intermediate representation
is necessary to build a reliable tool. To improve reliability we propose two methods.

While LLMs have captured interest for their open-endedness, we constrain the use of an LLM
to specific semantic extraction capabilities, such that we can quantify how well a model
performs at these testable capabilities. The benefit of using a large pretrained language model
is still that it does not require fine-tuning on a narrow data set to be able to perform.

The second method overlaps with the intermediate representation itself.
Such a representation is human-readable and helps explainability: 
the output of an application is computed from and over an auditable intermediate representation;
rather than from a document store with black-box model weights into a resulting text.
However, at scale, human introspection is not sufficient - even if the ability to spot-check
can boost confidence - and the ability to compute over the intermediate representation
can provide consistency checks. Such automated checks are important because the use of LLM
is guaranteed to hallucinate.

These hallucinations are controlled by the described two methods:
1. constraining the calls to better understood semantic evaluation capabilities,
and as such limiting the required output, as the probability of hallucination
for an auto-regressive LLM is lower-bound by an exponential in the number of tokens generated.
2. likelihood measures on consistency of generated elements of the representation.
While such consistency measures are confounded by both the risk of hallucination 
and the consistency of the source material, in either case these are elements of
the intermediate representation we want the application to review.

## Sketching an algorithm

Before outlining a proposal skeleton for an algorithm, we want to take a moment
to reflect on how we can reason about working with LLM function calls.
At the time of writing, integrating LLM function calls into a software stack
is still a novel field and these thoughts are shared in a spirit to collectively
help shape our mental models - not as a definitive rule.

### Thinking about the capabilities of function calls

It is out of scope for this document to do this question justice, but we just
want to cover the minimal point to be able to continue to describe the algorithm 
of interest.
From a (functional) programming perspective it is clear that calling
an LLM function (locally or over an API) is a deterministic, pure function
(for clarity of the argument we can set the temperature to zero).
The point we want to make is that, while that is a true characterisation of the function,
this is no longer a useful abstract to think about the function.
There are "too many variables to count" (for a human brain) in an LLM function for it
to be analysable as a pure function; nor is it a random function.
While the model weights taken individually for all accounts
are random, their collective effect clearly is not.

We propose that a helpful characterisation for functions is to talk about their capabilities.
It is clear that random functions, (computationally simple) pure functions and LLM calls all have 
different capabilities. When building an algorithm that uses different functions
with different capabilities, we will have to pay extra attention at the interfaces where functions
of different capabilities need to interact.

By being clear upfront about the capabilities we desire an (LLM) function to have,
we are also better positioned to reason about where we can replace
a more expensive (and possibly proprietary) model with a smaller, and cheaper open-source model,
once the algorithm itself has been demonstrated to function as intended.

This prelude hopefully illustrates the motivation to use LLM functions constraint
to semantic evaluations to build an intermediate representation. This constraint is
sufficient to achieve the goal of building such a representation, and conversely,
it allows us to compute a feedback on whether the semantic evaluation of the LLM
was sensible.

### Different types of world building

If we limit the use of LLM functions to semantic meaning extraction,
then we need to explicitly enumerate which types of questions we'll ask,
and be careful about the order in which they get asked.

While some types of questions become specific to the content of the text body,
we propose that initial grounding questions are more generic.

Specifically we find that it is first important to build up references.
While text is sequential, the referred to context is often not the immediately
preceding one, or even in the same document. By building up a representation
of where and how different segments of the text body are related, we can already
build a graph that allows us retrieve relevant context, or cluster and summarize
the text body. We can call this "Reference World Building".

A second type of questions we can ask, pertains to the content of a segment,
or segments of text. We can ask for the important entities and their relations
to be extracted in a structured form (see [Albert]). It is important to note here
that by doing this we are already extending the assumed capabilities of the model
beyond the simplest form of semantical meaning extraction. We find that a model like GPT4
is well capable to return meaningfully structured relations, however, we quickly see
that for larger segments it is more likely to omit information, that it may have been
keen to include on a different run.

So clearly we cannot just present a full text, and ask it to return a structured
representation. Other work also shows that while GPT4 can parse and reason over
linear, or tree-like graph relations, reasoning capabilities sharply decline 
for dense (and especially looped) relations [Momennejad, Santa Fe workshop 2023](https://www.youtube.com/watch?v=FQiAm5eSBIc).
To prelude onto later work, models like GPT4 (but not exclusively) can write
python code to reason over more complicated structures [Momennejad 2023, Voyager 2023].


 