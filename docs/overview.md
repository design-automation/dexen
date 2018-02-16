---
title: Overview
---

# Overview

Dexen hides the complexity of the server, nodes, and database from the user. This is highly desirable from a designer’s point of view. Installing Dexen either on a local network or on the Amazon is straight forward and requires minimal configuration. The user is then able to interact with Dexen via a web application in a web browser, or via an Application Programming Interface. A set of tasks can be defined and uploaded into Dexen, and the system will schedule and execute the tasks on a set of workers in parallel, with all data input and output automatically being stored in the database. The user is then able to view the data in the database, for example in order to download design variants that have been evolved.

Dexen achieves this ease-of-use due to the fact that the tasks only communicate via data. This allows the system to automatically discover which tasks to execute at any time. Each task can be executed multiple times and can create, modify, and delete data objects. Such data objects may contain any type of data – from simple types to arbitrary blobs of data, such as 3D models of design variants saved as files.

Despite the ease-of–use of Dexen, creating tasks still requires the user to write code. This is challenging for designers with limited programming skills. For example, in order to run an evolutionary optimization algorithm, procedures need to be written for starting and stopping the process as well as for the three main steps: development, evaluation, and feedback. To address this, I have developed a tool called Eddex, which requires no coding at all.
