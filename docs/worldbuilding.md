---
date: 12 July 2023
status: draft proposal v0.1
author: Benjamin Bollen
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

Specifically we find that it is first important to build up references and relations between segments of text.
While text is sequential, the referred-to context is often not the immediately
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
python code to reason over more complicated structures [Momennejad 2023, Voyager 2023], rather than to ask the model directly to do the reasoning.

After focusing a lens on the referential structure, and the content, more lenses can
be applied. Some may depend on the context and content of the text body.
In particular some lenses can also be meta-questions.
For example, who are the authors of the documents? In the use-case of discussion
forums, this can play a particularly relevant role, to map and build a model
of the contributors to the discussion.
Another example of a different world building effort can be to, given a desired goal,
try to conclude sensible options towards that goal; or in the context of governance,
try to draw the consensus landscape of where support lies.

It is important to stress that the original goal of this project (still) is to,
first, only achieve the first lens: can we better compress the structure of text
body; and, second, whether we can leverage an LLM to be able to generalise this ability
and improve its skills to do so. Skills in the sense of [Voyager2023].

It looks like the second lens of structuring the content can bear fruit too.
For each lens though, we have to understand the required capabilities and how
performance of the LLM capability can be estimated algorithmically.

## Pseudo-code for perception frames, groups and levels across lenses

We will present a scaffold to put our findings sofar together.
At the same time, it is a scaffold and as such there will be pieces
missing that we propose should be worked out and put in place.
However, to learn we must take small incremental steps,
so the aim is to have a minimal working tool.

Even though it is important to repeat that the project
is called "Discussion Trees", and the original use-case 
aims at better representing (governance) forum discussions,
we will try to generalise (possibly prematurely) in the interest of adjacent projects.
One such use-case is to structure more general knowledge bases,
and try to share thoughts on both use-cases.

One motivation to take on such risk is that there are early hands-on experiments (also confirmed [Albert])
that efforts to graph the content of knowledge base documents does lead to more succinct summerization.
This effect can be argued for, as the intermediate representation is a natural information bottleneck.
So while it might be ambitious to expect an ability to compute over
the intermediate representation of a general knowledge base,
relational querying and succinct representation can already be valuable in their own right.

### Perception frames

Any LLM model has a fixed context length. Most context lengths are 2k, up to 8k or even 32k tokens or beyond.
There is a clear motivation to have longer context length, and many works try to extend it.
These extensions come with an additional speed and memory cost, but it is an open question how
the quality of the attention can degrade over longer context lengths.
One outlier paper LongNet claims to achieve a context length of "1 billion tokens" (with diluted attention)
and measures the quality of the attention for different context lenghts 
with a perplexity measure (see Table 2 [LongNet2023](https://arxiv.org/pdf/2307.02486.pdf)).
To our understanding these matters are far from settled by the community,
and it is not our ambition to resolve them here.

We can conclude however that we want our algorithm to work with a finite context length,
and that we want to build representations for text bodies larger than that context length.

Our (LLM's) attention is not only limited by the context length;
also the specific world-building lens we have currently, "focuses our attention".

These are the first two reasons (context length, and question-type) to introduce
*perception frames*, or *frames*. Frames form a strict sequence such that
we have a tool to order and preserve which questions we ask over which pieces of text
from the text body.

In one frame we consider one *group* of text at a given *level* 
and with a given *world building question*.
We will construct these three terms in what follows.

In each additional frame we can navigate through the full body of text,
either by moving/jumping the location of the group,
changing the level (roughly, zooming in or out), or by asking a different type of question.
For initial implementations, we imagine to have very naive and hard-coded pathways.
We will simply slide the group iteratively through the text body at different levels,
and with different questions, and collect the outputs together in one graph database
as the intermediate representation.

### Groups

We define a group to be a list of text segments from the text body, $g_i$.

Much like the arguments to a function call (in most languages) we will assign meaning
to the order of these text segments. The specific function will depend on the level
and the question objective.

Looking ahead, following [Voyager2023], our path to generalising the ability to build
appropriate intermediate representations for novel text bodies, might even mean that
we don't know these prompt functions upfront. In [Voyager2023] they leverage the LLM
to write and refine (python / prompt) functions to learn and compose new skills.

For now though, a group is as simple an interface can be, and we can use this interface
to focus the attention as we build the intermediate representation.

### Levels

We will assume here that we deal with text bodies that are mostly well-formated strings.
Most language is written as punctuated sentences; if it concerns HTML, the HTML syntax is
correctly structured.

In the narrow use-case of discussions on forums, we have a starting advantage:
the conversation is already structured as posts (which can explicitly be segmented from the HTML).
In the case of general documents, our proposal is to use paragraphs as a *basic unit of text*.

We can propose the following three levels:
- level 0: group elements are sentences.
- level 1: group elements are basic units (ie. posts or paragraphs); and we consider only one unit.
- level 2+: group elements are still the basic units, but we have at least two of them.

We note that we opt for this notation, while in many ways it is less optimal.
First, while the authors would argue that it will be useful to be able to zoom into
specific sentences as the most granular level, thusfar it has become surprisingly difficult
to translate this into practical demonstrations that work.
So initially we will not consider level 0 with sentence level granularity.
In this situation, we could simplify the notation to:
> "a group of level $n$ has $n$ basic units".

This way a group of level $n$ is like an $n$-point function, that touches the text body
at $n$ points.

Basically, there is no over-arching principle that says this is the right approach;
rather this is a glove that fits the various experiments we've conducted so far
and as such is helpful to structure the code.
We elaborated on the concept of a "level 0", mostly to mark a placeholder for something
we don't know yet how to approach, but think is worth remembering for later.

## The approach

### step 1: parsing basic units

Given a text body, we segment it into *basic units*.
Within one document units are sequential, but clearly we lack an ordering
across documents.

In the use-case of a discussion forum we can treat threads as different documents,
where the posts are the basic units. In this case, we do have an additional time-ordering,
but we will ignore this: different people have not read all posts as soon as they are posted.
Similarly documents might be written at a certain time, and could be ordered;
but also here, a given author will not have read all documents written prior to their publishing date.

So we have different sequences of units, each built from a document (or thread) - by a standard parsing code.
We will come back to cross-document / cross-thread considerations once we've succeeded for intra-documents.

This step is "level 1 for structure building", effectively for free, completed with normal parsers.
In the context of documents, where the basic unit is a paragraph this is rather underwhelming.
While paragraphs in a well written text should express one point, ideas will likely elaborate over
multiple paragraphs, and higher order groups (or $n$-point functions) might be needed to bring it into scope.

In the context of discussion forums, however, we're given better "labelled data" as one post
is one contribution to the thread.

Nonetheless, by not relying on the LLM for the very first pass (level 1, structure),
we have a stable basis to start building up from.

We can store these units in the graph database with a $position$ in a $documentId$.
We add the "FOLLOWS" relation between two subsequent posts in the document;
and an "IN" relation for each unit to the document node itself.

### step 2: referencing basic units





[continue here]


 copyright © 2023 Benjamin Bollen. This work is licensed under a [CC0 license](https://creativecommons.org/publicdomain/zero/1.0/legalcode).