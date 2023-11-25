# Part 1

## Timing the exercise

I spent 3 hours (ish) on this exercise.

[Initial commit](https://github.com/kevinmartinjos/beats-to-prose/commit/8ab32fe2ce540a113399833cd94c9ca707470898) at 5.12 PM CET
[Final code commit](https://github.com/kevinmartinjos/beats-to-prose/commit/edea0da1919e409ddba85e4d7deb65cebb827fda) at 8.20 PM CET

I usually write more thoughtful commit messages and squash the commits where necessary. I haven't done that here in the interest of transparency.

## General approach
I used GPT-4 through openrouter due to the 32k context window size. The goal was to generate each beat one by one, supplying all the beats and the story-so-far as the context.
I experimented with 3 separate techniques:

1. [Simple Generator](https://github.com/kevinmartinjos/beats-to-prose/blob/main/generators/simple_generator.py), which simply concatenates all the beats together and makes a single request to openai, asking it to write the entire story in one go
2. [Sequential Generator](https://github.com/kevinmartinjos/beats-to-prose/blob/main/generators/sequential_generator.py), which generates each beat individually, supplying the story-so-far as the context.
3. [Interactive Generator](https://github.com/kevinmartinjos/beats-to-prose/blob/main/generators/interactive_generator.py), Same as the sequential generator, but allows the user to set a temperature and re-generate each beat using a different temperature if necessary. I was using this to basically test the sequential generation

Simple Generator worked surprisingly well. The result was coherent, but terse. Sequential Generator worked well, but is slow and expensive since I call the api `num_beats` times.
Sequential Generation had an occasional tendency to cut off sentences in the middle, but simply increasing `max_tokens` parameter to 300 (instead of 150) seems to have mitigated that.

I favor the sequential generator due to the following reasons:
1. I wanted to control the length and quality of each expanded beat individually
2. By asking the model to expand a specific beat, rather than all the beats simultaneously (and also by giving it the "story so far"), I expected to see more coherent results. I do find the quality better, but I do not have empirical evidence for this.

I did not attempt part 2.


## If you a month to work on this, how would you improve your approach?
I would fix some code smells:
- Introduce unit tests
- Instead of parsing yml directly to omegaconf, use dataclasses so that you can validate the config
- Use the streaming API instead of http calls. 

Then I would try out different ways to choose the "best" response from the model. For example, I can expand the same beat multiple times using different prompts, different temperature e.t.c and ask the LLM to rate it ([Gunasekar et. al](https://arxiv.org/abs/2306.11644)) and use that to re-rank the LLM response.
There are so many things we can try - happy to discuss them on a call.


## Running
Run `pip install -r requirements.txt` to install dependencies

### Simple Generator
```commandline
export OPENROUTER_KEY=<OPENROUTER API KEY>
python app.py -b beat_samples/scifi.txt -c configs/simple_scifi.yml
```

See `prose_samples/simple_scifi.txt` for an example output that used this config yml

### Sequential Generator
```commandline
export OPENROUTER_KEY=<OPENROUTER API KEY>
python app.py -b beat_samples/scifi.txt -c configs/sequential_scifi.yml
```

See `prose_samples/sequential_scifi.txt` for an example output that used this config yml

### Interactive Generator
```commandline
export OPENROUTER_KEY=<OPENROUTER API KEY>
python app.py -b beat_samples/scifi.txt -c configs/interactive_scifi.yml
```

At each beat, you will prompted for a temperature. Enter a value between 0 and 2 (I do not validate the input, sorry).
If you are happy with the generated prompty, enter `-1`, else type in another value between 0 and 2 to retry generation using that temperature.
See `prose_samples/interactive_scifi.txt` for an example output that used this config yml.

# Part 2

## What is your approach to producing prose that matches the parameters (i.e characters, setting, genre)?
In short, all this information should be part of the context. GPT-4 has a context window of 32k, GPT-4 turbo has a context window of 128k.
Hence our backstories will fit in the model's context.
We can, however, help the model out by including only the relevant backstory. For example, if the beat is "Jack starts drilling the surface", then we can do a simple exact string match to figure out that the only character mentioned in the beat is "Jack", and include only his background story in the context
We can even train a model to do this - given 1000 backstories, pick the top-10 backstories relevant for this given beat. For each of the 1000 backstories the model would predict `1` (include) or `0` (do not include)


## What models would you use? Why?
If cost and latency is not a consideration, I'd stick to the models from Open AI (GPT-4, specifically).
None of the open source alternatives (including Llama-2) has in my experience matched GPT-4 in quality.
However, any recent LLM with a large enough context size (eg: 16k) would allows us to get decent results.

## If you need to fine-tune or train, how would go about doing that? What data would you use?
The first thought that comes to my mind is summarization datasets. What we are doing is the reverse of summarization - i.e we take in a short beat and expand it.
I do not know if there are any creative fiction summarization datasets though.
I can synthetically create one - take a book (or a chapter), ask a model to summarize it - that's your beat. Now use the generated beat as an input while fine-tuning and use the full-chapter of the book as the supervision signal

## How would you prepare the data?
convert numbers to words, convert all the dates to a single format e.t.c.
I will also need to choose a tokenizer. I'm not sure if that's the kind of answer you are looking for - let's discuss.

## How would you evaluate whether the generations are good quality and fits the parameters
Some ideas:

1. Use another LLM to grade the response.
2. Use something like n-gram overlap to see if words in the beat are indeed present in the expanded prose
3. Use a summarization model to summarize the generated prose. How close is the summary to the original beat?
4. User feedback (eg: thumbs up and thumbs down buttons)

## What about cost and latency considerations?
As long as the model is hosted by a third party, latency is to a certain extent out of our control. We can, however, have some control over latency through:
1. Shortening our input. The smaller the context the model has to parse, the faster it can respond.
2. Use a streaming API. This will reduce the perceived latency
3. Make as few round trips/network calls as possible. For example, rather than expand each beat separately, we can adopt a 2-pass approach. That is, do a "generation pass" where the model expands all the prompts simultaneously, and then do an "edit pass" where we instruct the model to revise parts of the already generated text. 