# SimZ: A Conceptual Guide

## Introduction

This document provides a comprehensive conceptual guide to SimZ, combining explanatory text with visual diagrams to help you understand the philosophy, design principles, and mental models behind the simulation system. Rather than focusing on technical implementation details, this guide explains how to think about and approach simulation design in SimZ.

The visual diagrams throughout this document use Mermaid syntax and can be rendered in many markdown viewers that support it, including GitHub and GitLab.

## Table of Contents

1. [Introduction](#introduction)
2. [SimZ Architecture Overview](#simz-architecture-overview)
3. [Understanding Discrete Event Simulation](#understanding-discrete-event-simulation)
   - [The Essence of Discrete Event Simulation](#the-essence-of-discrete-event-simulation)
   - [Time in SimZ](#time-in-simz)
4. [Components: The Building Blocks of SimZ](#components-the-building-blocks-of-simz)
   - [What is a Component?](#what-is-a-component)
   - [Types of Components](#types-of-components)
   - [Component Behavior](#component-behavior)
   - [Component State and Execution](#component-state-and-execution)
5. [Workflows: Connecting the Dots](#workflows-connecting-the-dots)
   - [From Components to Systems](#from-components-to-systems)
   - [Connections and Routing](#connections-and-routing)
   - [The Mental Model of Workflows](#the-mental-model-of-workflows)
6. [Entities: What Flows Through the System](#entities-what-flows-through-the-system)
   - [Understanding GenTypes](#understanding-gentypes)
   - [Entity Attributes](#entity-attributes)
   - [Containers: The Carriers](#containers-the-carriers)
7. [Designing Simulations: The Mental Model](#designing-simulations-the-mental-model)
   - [Thinking in SimZ](#thinking-in-simz)
   - [From Real World to Simulation](#from-real-world-to-simulation)
   - [The Iterative Approach](#the-iterative-approach)
8. [Project Structure](#project-structure)
9. [Practical Example: Coffee Shop Simulation](#practical-example-coffee-shop-simulation)
10. [Conclusion: The SimZ Philosophy](#conclusion-the-simz-philosophy)
11. [Notes on Using These Diagrams](#notes-on-using-these-diagrams)

## SimZ Architecture Overview

Before diving into specific concepts, let's look at the overall architecture of SimZ to understand how the different components fit together.

The following diagram illustrates the core components of the SimZ architecture and their relationships:

![c_1](/1_c.svg)

This diagram shows how the Project Manager coordinates the File Manager and DB Manager, while the Simulation Builder orchestrates the Component System, GenType System, and Workflow Graph to create and run simulations.

## Understanding Discrete Event Simulation

### The Essence of Discrete Event Simulation

At its heart, discrete event simulation is about modeling the world as a series of distinct events that occur at specific points in time. Unlike continuous simulation (which models systems that change continuously over time), discrete event simulation jumps from one event to the next, skipping over periods where nothing changes.

Think of it like watching a time-lapse video of a busy restaurant:

- A customer arrives (event)
- They wait in line (state)
- They order food (event)
- The chef prepares the meal (process)
- The food is served (event)
- The customer eats and leaves (events)

In this example, we don't need to simulate every second of the day—we only care about the moments when something meaningful happens. This makes discrete event simulation both efficient and powerful for modeling complex systems.

The following Gantt chart visualizes how a discrete event simulation timeline works, showing how the simulation clock jumps from one event to the next:

![c 2](/c_2.svg)

Notice how the simulation focuses only on the specific events, with the clock jumping directly from one event to the next rather than simulating every moment in between.

### Time in SimZ

In SimZ, time is abstract and flexible. A time unit could represent a second, minute, hour, or any other interval depending on what makes sense for your simulation. The simulation clock advances from one event to the next, skipping over periods where nothing happens.

This approach allows SimZ to efficiently simulate processes that might take days, weeks, or even years in the real world, compressing them into seconds of computation time.

## Components: The Building Blocks of SimZ

### What is a Component?

Components are the fundamental building blocks of any SimZ simulation. Think of components as specialized workers or machines in a factory, each with a specific job to do. Each component:

1. **Receives** entities (like a worker receiving materials)
2. **Processes** them according to defined rules (like a worker performing their task)
3. **Sends** them to the next component (like passing the work to the next station)

Components encapsulate behavior, making your simulation modular and easier to understand. They're like LEGO blocks that you can connect in different ways to build complex systems.

The following diagram illustrates how components interact with entities in a typical workflow:

![c 3](/c_3.svg)

This diagram shows how a Generator creates entities that flow through Resources, getting processed and updated at each step before eventually exiting the system.

### Types of Components

While SimZ allows for custom component types, there are two fundamental types that form the backbone of most simulations:

1. **Generators**: These create entities and introduce them into the simulation. Think of generators as the "entry points" to your system—like customers arriving at a store, products entering a factory, or calls coming into a call center.

2. **Resources**: These process entities with capacity constraints. A resource might represent:
   - A server that can only handle one request at a time
   - A team of workers who can process multiple tasks simultaneously
   - A machine with limited capacity
   - A waiting area with a maximum capacity

Resources capture the essence of real-world constraints: limited capacity, processing time, and queuing behavior.

### Component Behavior

Each component has its own behavior that defines how it interacts with entities. This behavior can be as simple or complex as needed:

- A generator might create entities at regular intervals or according to a statistical distribution
- A resource might process entities in a first-come-first-served manner or according to priority
- Processing times might be fixed or variable based on entity attributes

The beauty of components is that they hide this complexity behind a simple interface, making it easier to build and understand complex simulations.

### Component State and Execution

Components transition through different states during simulation execution. Understanding these states helps you grasp how components operate over time:

![c4](/c_4.svg)

This state diagram shows the different states a component can be in and the transitions between them. Note how resources can queue entities when they're busy, a key aspect of resource-constrained systems.

## Workflows: Connecting the Dots

### From Components to Systems

Individual components are powerful, but the real magic happens when you connect them together to form workflows. A workflow is simply a network of connected components that defines how entities flow through your simulation.

Think of a workflow like a flowchart or a map:

- It shows the possible paths entities can take
- It defines the relationships between components
- It captures the overall structure of your system

### Connections and Routing

Components connect to each other through defined pathways, much like roads connect locations in a city. These connections determine:

- Where entities go after being processed by a component
- Which types of entities can flow along which paths
- How entities are routed when multiple paths are available

The workflow structure can be as simple as a linear sequence (A → B → C) or as complex as a highly interconnected network with branches, loops, and conditional routing.

### The Mental Model of Workflows

When designing workflows in SimZ, it helps to think in terms of flow and process:

- Where do entities enter the system?
- What steps do they go through?
- Where might bottlenecks occur?
- How do entities exit the system?

Visualizing your workflow as a diagram can help you understand and communicate the structure of your simulation.

## Entities: What Flows Through the System

### Understanding GenTypes

In SimZ, the things that flow through your simulation are called entities, represented by the GenType system. These entities can represent virtually anything:

- Customers in a service simulation
- Products in a manufacturing simulation
- Calls in a call center simulation
- Packets in a network simulation
- Patients in a healthcare simulation

Entities are more than just objects—they carry information (attributes) that can influence how they're processed.

### Entity Attributes

Each entity has attributes that define its characteristics and state. For example:

- A customer entity might have attributes like "patience level" or "service requirements"
- A product entity might have attributes like "size," "weight," or "completion percentage"
- A patient entity might have attributes like "severity," "treatment needs," or "arrival time"

These attributes can change as the entity moves through the simulation, reflecting how real-world objects change state as they go through processes.

### Containers: The Carriers

Entities don't travel alone—they're wrapped in containers that provide additional context:

- Where the entity came from
- Where it's going next
- How it should be handled

Think of containers as the envelopes that carry letters through a postal system—they contain both the content (the entity) and the routing information needed to get it to its destination.

The following class diagram illustrates the structure of entities and their relationship to containers and workflows:

![c_5](/c_5.svg)

This diagram shows how GenContainers hold GenTypes (entities) and how the Workflow routes these containers between components.

## Designing Simulations: The Mental Model

### Thinking in SimZ

When designing simulations in SimZ, it helps to adopt a specific mental model:

1. **Identify the entities**: What are the things flowing through your system?
2. **Define their attributes**: What characteristics do these entities have?
3. **Map the process**: What steps do entities go through?
4. **Identify the resources**: What constraints exist in your system?
5. **Define the behaviors**: How do components interact with entities?

This process-oriented thinking helps you break down complex systems into manageable pieces.

The following diagram illustrates the mental model for designing simulations in SimZ:

<img src="/c_6.svg" alt="c6" width="600" />

Notice the iterative nature of the process, where you refine your model based on simulation results.

### From Real World to Simulation

Translating real-world systems into SimZ simulations involves abstraction—focusing on the elements that matter for your analysis and simplifying the rest. Ask yourself:

- What level of detail is necessary?
- Which factors significantly impact the behavior of the system?
- What metrics are you interested in measuring?

Not everything needs to be modeled explicitly. The art of simulation is knowing what to include and what to abstract away.

### The Iterative Approach

Building effective simulations is typically an iterative process:

1. Start with a simple model that captures the core elements of your system
2. Run the simulation and analyze the results
3. Identify areas where the model doesn't match reality or your expectations
4. Refine the model by adding detail where needed
5. Repeat until the simulation provides useful insights

This iterative approach allows you to build understanding gradually, rather than trying to create a perfect model from the start.

## Project Structure

SimZ organizes simulation projects in a structured way to manage files and data effectively. Understanding this structure helps you navigate and work with your simulation projects.

The following diagram illustrates the typical project structure in SimZ:

![c7](/c_7.svg)

This structure shows how a project contains configuration files, run data, and saved state information, providing a complete record of your simulation setup and results.

## Practical Example: Coffee Shop Simulation

To illustrate how these concepts come together, let's look at a practical example: a coffee shop simulation. This example shows how different components interact to model a real-world system.

<img src="/c_8.svg" alt="c8" width="600" />

In this example:

- Customer Generator creates Customer entities that enter the system
- Order Queue holds customers waiting to place orders
- Barista Resource processes orders with limited capacity
- Pickup Counter holds completed orders
- Supply Generator creates inventory items
- Inventory stores supplies needed for making drinks

This workflow captures the essential elements of a coffee shop operation while abstracting away unnecessary details.

## Conclusion: The SimZ Philosophy

The core philosophy of SimZ can be summarized in a few key principles:

1. **Modularity**: Break complex systems down into understandable components
2. **Flow-based thinking**: Focus on how entities move through the system
3. **Event-driven**: Model the world as a series of discrete events rather than continuous change
4. **Abstraction**: Include the details that matter and simplify the rest
5. **Visualization**: See and understand your system through interactive visualization

By embracing these principles, you can use SimZ to gain insights into complex systems, identify bottlenecks, test improvements, and make better decisions based on a deeper understanding of how your systems behave under different conditions.

Remember that simulation is both a science and an art—it requires technical knowledge, but also creativity and judgment in how you model the world. The goal isn't to create a perfect replica of reality, but rather a useful model that helps you understand and improve the systems you care about.

## Notes on Using These Diagrams

These diagrams are created using Mermaid, a markdown-based diagramming tool. They can be rendered in many markdown viewers that support Mermaid syntax, including GitHub, GitLab, and various markdown editors.

The diagrams provide visual representations of:

1. The overall SimZ architecture
2. How discrete events work in a timeline
3. How components interact with entities
4. A practical workflow example (coffee shop)
5. The structure of entities and their flow
6. The mental model for designing simulations
7. Component states and execution flow
8. The physical project structure

These visuals complement the conceptual explanations by providing a way to see the relationships between different elements of the SimZ system.
