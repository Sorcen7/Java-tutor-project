# Simulation Log: Lab 15.3 Wordle Solver
**Session ID**: `1763e33e-9c0b-4617-a892-8447dbd4b72d`
**Date**: 2025-12-28 19:50:26

## Turn 1
**Student**: I need to read `words.txt` into a list.

**Tutor** (4.74s):
You want to load the words from the "words.txt" file into your ArrayList. 

To do this, you can use a `Scanner` object to read the file line by line and add each word to the list. Here's a template to get you started:

```java
// Initialize the Scanner object
Scanner sc = new Scanner(new File("words.txt"));

// Loop through each line in the file
while(sc.hasNext()) {
    // Add the current line (word) to the ArrayList
    words.add(sc.next());
}

// Don't forget to close the Scanner when you're done!
sc.close();
```

What do you think happens next?

---
## Turn 2
**Student**: Should I use an Array or ArrayList?

**Tutor** (4.42s):
Since you're working with a list of words, it's more convenient and flexible to use an `ArrayList` instead of a regular array. 

Here's why:

* An `ArrayList` can grow dynamically as you add more elements, whereas an array has a fixed size that you need to specify at compile-time.
* With an `ArrayList`, you don't have to worry about manually resizing the array or checking for bounds when accessing its elements.

So, in this case, using an `ArrayList` will make your life easier and give you more flexibility.

---
## Turn 3
**Student**: Okay ArrayList. How do I use Scanner to read it?

**Tutor** (6.04s):
To read the words from the "words.txt" file into an `ArrayList`, you can use a `Scanner` object to iterate through each line in the file, split each line into individual words (assuming they're separated by spaces), and add them to your list.

Here's how:

```java
// Initialize the ArrayList to store the words
ArrayList<String> words = new ArrayList<>();

// Initialize the Scanner object
Scanner sc = new Scanner(new File("words.txt"));

// Loop through each line in the file
while(sc.hasNextLine()) {
    // Read the current line (word) from the file
    String word = sc.nextLine();

    // Add the word to the ArrayList
    words.add(word);
}

// Don't forget to close the Scanner when you're done!
sc.close();
```

What do you think happens next?

---
## Turn 4
**Student**: Wait, does `Scanner` automatically close or do I need to close it?

**Tutor** (4.94s):
In Java, it's generally a good practice to explicitly close resources like `Scanner` objects when you're done using them. This is because the garbage collector might not always be able to clean up these resources for you.

So, in this case, you should manually close the `Scanner` object after you've finished reading from the file:

```java
// Initialize the Scanner object
Scanner sc = new Scanner(new File("words.txt"));

// ... (rest of your code)

// Close the Scanner when you're done!
sc.close();
```

This ensures that any system resources associated with the `Scanner` are properly released.

---
