<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=180&color=0:0D1117,50:1F6FEB,100:58A6FF&section=header&text=Krishna%20Sriharsha&fontSize=44&fontColor=FFFFFF&fontAlignY=32&desc=Machine%20Learning%20Engineer%20%C2%B7%20Systems%20Builder&descSize=16&descAlignY=54&animation=fadeIn" width="100%" alt="header" />

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&pause=1400&color=58A6FF&center=true&vCenter=true&width=620&lines=Models+are+the+easy+part.;I+build+the+systems+around+them.;Graph+databases%2C+APIs%2C+benchmark+pipelines." alt="What I do" />

<br />

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gksriharsha/)
[![Medium](https://img.shields.io/badge/Medium-000000?style=for-the-badge&logo=medium&logoColor=white)](https://gksriharsha.medium.com/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/gksriharsha)

<img src="https://komarev.com/ghpvc/?username=gksriharsha&style=for-the-badge&color=1F6FEB&label=PROFILE+VIEWS" alt="profile views" />

</div>

<br />

## About

I work at the seam between machine learning and infrastructure — the part where a model has to live inside a real API, query a real database, and answer in real time.

Most of what I build starts as a question I couldn't find a clean answer to. *How do you actually store a family tree so that "second cousin twice removed" is one query instead of ten?* *How fast is the same classifier in Python versus Java versus C, honestly measured?* The repos below are those questions, worked out in code.

```text
  Focus       Machine learning systems, graph data modeling, backend APIs
  Building    Flask + JanusGraph traversal engine for arbitrary family structures
  Exploring   Vector search, distributed training, MLOps tooling
  Writing     Long-form build logs on Medium — Gremlin, layout algorithms, feature selection
```

<br />

## Why a graph database

Resolving "first cousins" in a relational schema takes several self-joins and a recursive CTE. In a graph it is a single traversal: walk up two `child_of` edges, then back down two. Below is that query running against the family tree.

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/traversal-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/traversal-light.svg" />
  <img src="assets/traversal-dark.svg" alt="An animated Gremlin traversal walking up two generations and back down a family tree, lighting up the first cousins it finds" width="100%" />
</picture>

</div>

<br />

## Tech

<table>
<tr>
<td valign="top" width="50%">

**Machine Learning**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)

</td>
<td valign="top" width="50%">

**Backend**

![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![Groovy](https://img.shields.io/badge/Groovy-4298B8?style=flat-square&logo=apachegroovy&logoColor=white)
![REST](https://img.shields.io/badge/REST_APIs-6E4C9F?style=flat-square&logoColor=white)

</td>
</tr>
<tr>
<td valign="top" width="50%">

**Data & Storage**

![JanusGraph](https://img.shields.io/badge/JanusGraph-2C6B9E?style=flat-square&logoColor=white)
![Gremlin](https://img.shields.io/badge/Gremlin-1B9E77?style=flat-square&logoColor=white)
![Cassandra](https://img.shields.io/badge/Cassandra-1287B1?style=flat-square&logo=apachecassandra&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)

</td>
<td valign="top" width="50%">

**Frontend & Tooling**

![Angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)

</td>
</tr>
</table>

<br />

## Projects

<table>
<tr>
<td width="50%" valign="top">

### 🌳 Family Tree

A genealogy engine built on a **graph database** instead of a relational one — so "who is my great-grandmother's brother?" is a single Gremlin traversal, not a pile of recursive joins. Includes an auto-layout algorithm that keeps generations readable no matter how tangled the tree gets.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white)
![JanusGraph](https://img.shields.io/badge/JanusGraph-2C6B9E?style=flat-square)

**[API →](https://github.com/gksriharsha/Flask-Family-Tree)** &nbsp;·&nbsp; **[UI →](https://github.com/gksriharsha/Family-Tree-UI)** &nbsp;·&nbsp; [Write-up](https://gksriharsha.medium.com/designing-the-layout-of-a-family-tree-2-ff226aa40152)

</td>
<td width="50%" valign="top">

### ❄️ Svalbard

A seed vault for ML benchmarks. Runs the *same* classification task across languages and frameworks, then records runtime and accuracy in one queryable database — so "which is faster" stops being folklore and starts being data.

![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)

**[Core →](https://github.com/gksriharsha/Svalbard)** &nbsp;·&nbsp; **[Service →](https://github.com/gksriharsha/Svalbard-SpringBoot)**

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📉 RSFS

**Random Subset Feature Selection** — a dimensionality-reduction algorithm that scores features by how often they prove useful across many random subsets, rather than ranking them one at a time. Implemented in Python, with a full write-up of the method.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)

**[Repo →](https://github.com/gksriharsha/RSFS)** &nbsp;·&nbsp; [Paper walkthrough](https://gksriharsha.medium.com/random-subset-feature-selection-a-dimensionality-reduction-approach-8f2b3876acd8)

</td>
<td width="50%" valign="top">

### 🎛️ Classifier Workbench

A desktop GUI for throwing one dataset at several classifiers at once and comparing them side by side — so model selection becomes something you *look at* rather than something you script from scratch every time.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)

**[GUI →](https://github.com/gksriharsha/MultipleClassifier-GUI)** &nbsp;·&nbsp; **[Pipeline →](https://github.com/gksriharsha/AutomatedLearning)**

</td>
</tr>
</table>

<br />

## Writing

I write long-form build logs — the reasoning and the dead ends, not just the finished code.

- [10 Most Used Functions in Gremlin](https://gksriharsha.medium.com/10-most-used-functions-in-gremlin-3-3c121da6d958) — the traversal vocabulary that covers 90% of real graph queries
- [Designing the Layout of a Family Tree](https://gksriharsha.medium.com/designing-the-layout-of-a-family-tree-2-ff226aa40152) — why generic graph layout algorithms fail on genealogies
- [Random Subset Feature Selection](https://gksriharsha.medium.com/random-subset-feature-selection-a-dimensionality-reduction-approach-8f2b3876acd8) — a dimensionality reduction approach

**[All posts on Medium →](https://gksriharsha.medium.com/)**

<br />

## Stats

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stats-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/stats-light.svg" />
  <img src="assets/stats-dark.svg" alt="Contribution counts and language breakdown, regenerated daily from the GitHub API" width="100%" />
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com?user=gksriharsha&hide_border=true&background=0D1117&stroke=30363D&ring=58A6FF&fire=58A6FF&currStreakLabel=58A6FF&sideLabels=C9D1D9&currStreakNum=C9D1D9&sideNums=C9D1D9&dates=8B949E" />
  <source media="(prefers-color-scheme: light)" srcset="https://streak-stats.demolab.com?user=gksriharsha&hide_border=true&background=FFFFFF&stroke=D0D7DE&ring=1F6FEB&fire=1F6FEB&currStreakLabel=1F6FEB&sideLabels=24292F&currStreakNum=24292F&sideNums=24292F&dates=57606A" />
  <img src="https://streak-stats.demolab.com?user=gksriharsha&hide_border=true" alt="Contribution streak" />
</picture>

</div>

<br />

## Let's talk

I'm open to **machine learning and backend engineering roles**, and to collaborating on anything involving graph data, ML infrastructure, or benchmarking systems honestly.

The fastest way to reach me is LinkedIn — or open an issue on any repo here if it's about the code.

<div align="center">

[![LinkedIn](https://img.shields.io/badge/Message_me_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gksriharsha/)
<!-- Add your email below if you want it public — replace the address, then delete this comment.
[![Email](https://img.shields.io/badge/Email_me-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:you@example.com)
-->

</div>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=120&color=0:58A6FF,50:1F6FEB,100:0D1117&section=footer" width="100%" alt="footer" />

<sub>Thanks for scrolling this far.</sub>

</div>
