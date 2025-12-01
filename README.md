# Project Harmonica

## What is Project Harmonica?

**Project Harmonica** is a research project by me, Josiah Huergo. 

It is comprised of several different inter-related explorations into music theory, mathematics and computer science.

While there isn't a single unified goal for this project, there are some foundational guiding ideas, such as:

- Exhaustively accounting for all combinatorial possibilities is *fun*
- Teaching computers how to reason about musical objects & make music is *fun*
- Exploring the mathematical structures that can model musical expression is *fun*
- In general, the intersection between music theory, mathematics and computer science is **FUN!**

## What is its scope?

Although this project is rather intersectional, there have proven to be some consistent limits to its scope.

This project is oriented around 12EDO - that is to say, 12 tone equal temperament - music. Although the pitch structures found in this project are usually abstract and flexible enough to apply to non-12 EDOs, I personally don't spend very much time playing around with xenharmony. I simply have plenty to keep me occupied in 12EDO!

In this project, pitch values are represented by integers, and time values (onsets and durations) are represented by rational numbers (AKA fractions). 

These are not hard limits or anything - it is simply the scope that has emerged and remained consistent over time. The project is an evolving thing.

## History of Project Harmonica

### Josiah discovers interval cycles

This project started in 2019, when I began exploring cycles of intervals on the piano. I had noticed that when you build a major chord, you start on one note and then move up 4 semitones, and then 3 semitones. But if I kept going up 4 semitones, then, 3, then 4, then 3, over and over, it created this really lovely pattern. 

From there, I kept studying this pattern to realize that eventually, the cycle would repeat, and I'd end up going through all the same notes again. Not only that, but this pattern went through every note twice, and in it I would find every major and minor chord, including all extensions. This was very beautiful to me! 

Soon enough, I began exploring what patterns emerged if I used numbers other than 4 and 3 - such as 2 and 5, or 1 and 3, or 5 and 6, etc. I eventually realized that this was, on some level, *identical* to my concept of what scales were.

### Automating exploration with computers

These explorations started out with just a piano and a notebook. It didn't take long for me to begin experimenting with using Python to capture my processes, realizing how much of it was purely algorithmic. 

Part of my motivation was to explore what was musically possible for me, like building out a geographic map of some greater musical world. This naturally led me to combinatorics. In 2020, I became aware of the concept of the combinatorial necklace, which represents a circular arrangement of objects where all rotations are equivalent. This, to me, clearly modeled the way I conceptualized what a musical scale was.

### Trying out different languages

From 2020 through 2025, I ended up learning more about math and programming. Seeing that my explorations were interconnected and broad, I tried repeatedly to unify them into a single project. 

From a Python library, to an Obsidian wiki, to a Rust library, to a SuperCollider library, I jumped around using different tools and envisioning the project taking different shapes. 

One of my main inspirations of CDP - the **Composer's Desktop Project**. CDP is a collection of tools for the manipulation and analysis of sound, primarily geared towards composition. I always admired the organization of the project, and wished to create my own similar toolkit, but for my music-math explorations.

Over time, I began to realize that there is a lot of potential for algorithmically generating music in my project, and began focusing on that as well.

### Where we are now

In its current form, Project Harmonica consists of two main parts:

1. A collection of Jupyter Notebooks
2. A Python library

These notebooks are where multiple things occur:

- Brainstorming and scratch work, where ideas are explored and new tools emerge
- Demonstration and documentation, where research is compiled and tool usage is demonstrated

And the Python library (the `harmonica` package) is essentially a toolkit that emerges from the research, where objects and algorithms are organized into one system, enabling further research.

## What's on the horizon?

One of my main goals is to fill out and refine **as much documentation as possible**, in the form of Jupyter notebooks. 

This does two things:

1. It makes it easier for me to pick the project back up when I take breaks.
2. It makes it easier for others to pick this project up and see what it's about.

Another goal is to keep **iterating on the organization of the library**.

I have plenty of existing ideas to elaborate on, but I will explore any new ideas that pique my interest.

### Ideas that are much more lofty

There are much larger ideas I've had in mind for a while, but they would take significant time and energy, and I worry that I couldn't pull them off alone.

The (relatively) easier one is to develop my own **domain-specific language** for this project. An interpreted language that is specifically oriented to the things I do in this project.

The more difficult one is to develop a full GUI application as a sort of all-in-one laboratory for this research. Something with a piano roll, a console, a text editor, and notebooks (for combining code and markdown), and various other visualizations for different concepts - something that would integrate the aforementioned Harmonica language. 

I will no doubt make attempts to bring these ideas to life, but I am under no illusion about the difficulty of these goals. Making a programming language is a lot of work. Making a big, complex GUI application is an insane amount of work.

Even if I never bring these more lofty ideas to fruition, I will still labor away happily on the existing shape of the project. It is sufficient.

## The structure of this repository

`harmonica` contains the Python package, where `notebooks` is where a vast majority of the documentation and research can be found. `tests` contains unit tests for the `harmonica` package.
