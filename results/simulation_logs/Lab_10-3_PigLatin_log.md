# Simulation Log: Lab 10.3 PigLatin
**Session ID**: `1b9c5b05-5eb8-41eb-8684-59d50dfa59b8`
**Date**: 2025-12-28 19:50:57

## Turn 1
**Student**: I'm detecting vowels.

**Tutor** (3.25s):
You're on the right track! So, you have a method `isVowel(char c)` that checks if a character is a vowel or not. That's great!

Now, let's think about how we can use this method to solve the Pig Latin problem. Do you think we could use it to find the first vowel in a word?

---
## Turn 2
**Student**: I am using `if x == 'a'` but it breaks.

**Tutor** (2.83s):
You're trying to detect vowels by comparing the character `x` with `'a'`. However, this approach won't work as expected.

Can you think of why not?

(Hint: It has something to do with case sensitivity and ASCII values.)

---
## Turn 3
**Student**: Okay, I fixed that. How do I output the result?

**Tutor** (4.13s):
You've got the vowel detection working!

Now, let's talk about how to output the results. You can use `System.out.println()` or `System.out.print()` to print out the vowels you found.

But wait! What if you want to format the output in a specific way?

That's where `printf()` comes in! It allows you to specify the formatting of your output, like how many decimal places to show for numbers or how to align text.

Can you think of how you might use `printf()` to print out the vowels you found?

---
