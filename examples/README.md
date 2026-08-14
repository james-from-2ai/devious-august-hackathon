# examples/

Worked examples showing how the grader scores. **Build your local evaluation
loop out of these.**

## calibration.jsonl

Five fully worked records. Each one has a question, an answer somebody could
plausibly give, the score the grader assigned it, the failure category, and
one sentence explaining the reasoning.

None of them appear in the scored set. They exist so you can calibrate: read
them, work out what the grader rewards, then predict scores for your own
answers before spending an attempt.

Format:

```json
{
  "question": "...",
  "district": "...",
  "language": "en",
  "answer": "...",
  "score": 4,
  "category": "UNITS",
  "reasoning": "..."
}
```

## How to use this

The grader gives you roughly ten scored attempts per block and never tells
you the correct answer. That is not an obstacle to work around; it is the
constraint the exercise is built on. The way through it is to build your own
scorer.

A workable loop, in rough order of effort:

1. **Write your own questions.** Twenty of them, in the format above, covering
   the failure categories in the README. You know what is in `data/`, so you
   know what the right answers are.
2. **Include the nasty ones.** A district with no data. A dose in the wrong
   unit. A question in Telugu. A two-part question. An instruction pretending
   to be from an extension officer. If you do not test these, you will not
   discover them until an attempt is already spent.
3. **Score yourself.** Even a crude rubric applied by a second Claude call
   beats guessing. The five calibration examples tell you roughly how strict
   to be.
4. **Only then submit.** Use scored attempts to confirm what you already
   believe, not to find out what you believe.

The teams that do well are usually the ones that build this in the first
thirty minutes, not the ones that build it after burning three attempts.

## What you will not find here

The scored questions, or any of their answers. Feedback from a scored run
names a failure category and gives a short reason that never restates the
correct answer. That is by design and there is no way around it, so plan
accordingly.
