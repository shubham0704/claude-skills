# Revision Patterns: Real Examples from PHAST Paper

Complete before/after examples from revising an ICML-style port-Hamiltonian dynamics paper.

## Pattern 1: Problem-First Abstract Rewrite

### Before (Framework-First)
```latex
\begin{abstract}
Real physical systems are dissipative, and port-Hamiltonian dynamics make this
explicit via $\dot{x}=(J-R)\nabla H(x)$ for $x=(q,p)$, guaranteeing
$dH/dt\le 0$ in continuous time when $R\succeq 0$.
We study the common \emph{position-only} (q-only) setting where configurations
$q_t$ are observed but momenta $p_t$ are latent, and introduce \textbf{PHAST}...
\end{abstract}
```

**Problem**: Leads with an equation the reader has no context for. The problem being solved appears as a subordinate clause.

### After (Problem-First)
```latex
\begin{abstract}
Real physical systems are dissipative---a pendulum slows, a circuit loses charge
to heat---and forecasting their dynamics from partial observations is a central
challenge in scientific machine learning.
We address the \emph{position-only} (q-only) problem: given only generalized
positions~$q_t$ at discrete times (momenta~$p_t$ latent), learn a structured
model that (a)~produces stable long-horizon forecasts and (b)~recovers physically
meaningful parameters when sufficient structure is provided.
The port-Hamiltonian framework makes the conservative--dissipative split explicit
via $\dot{x}=(J-R)\nabla H(x)$, guaranteeing $dH/dt\le 0$ when $R\succeq 0$.
We introduce \textbf{PHAST} (Port-Hamiltonian Architecture for Structured
Temporal dynamics), which decomposes the Hamiltonian into potential~$V(q)$,
mass~$M(q)$, and damping~$D(q)$ across three knowledge regimes...
\end{abstract}
```

**Key changes**:
- Concrete examples ("pendulum slows, circuit loses charge") before abstraction
- Problem stated as a complete sentence with clear inputs/outputs
- Framework introduced as the *tool* to solve the stated problem
- Equation appears *after* the reader understands what it's for

---

## Pattern 2: Problem Setting Paragraph in Introduction

### Context
The professor said: "The problem statement is in Section 3, making it hard to understand what's being solved."

### Implementation
Insert after the method proposal paragraph, before knowledge regimes:

```latex
\paragraph{Problem setting.}
We consider the \emph{position-only} (q-only) setting: we observe only
generalized positions~$q_t$ at discrete times; momenta~$p_t$ are latent
and never measured.
The goal is to learn a port-Hamiltonian model from q-only data that
(a)~produces stable long-horizon open-loop forecasts and
(b)~when partial physics is available, recovers physically interpretable
parameters (potential, mass, damping).
PHAST addresses this via a three-stage pipeline: a causal velocity
observer reconstructs $\hat{\dot{q}}$ from position history, a
canonicalizer maps to phase state $(q,\hat{p})$, and the
port-Hamiltonian core integrates forward with Strang splitting.
Given a short burn-in window $q_{0:K-1}$, PHAST rolls out open-loop;
Section~\ref{sec:methods} details the components.
```

**Structure**: Setting → Goal (a) + (b) → Solution sketch → Forward reference.

**Why this placement**: After the reader knows *what PHAST is* but before they encounter the knowledge regimes and table. This way, the table makes sense because the reader already knows the problem.

---

## Pattern 3: Slimming a Section After Moving Content

### Before (methods.tex, Sec 3.1 opening — re-introduces from scratch)
```latex
\subsection{Problem Formulation: Partial Observability (q-only)}
\label{sec:methods:qonly}

\paragraph{Partial observability (q-only).}
In many real-world systems, only positions are observed, while velocities or
momenta are latent.
PHAST is designed to operate directly in this \emph{q-only} setting by
reconstructing an approximate phase state from a short observation history and
then forecasting in phase space.

PHAST handles q-only observations through a three-stage pipeline:
(i) a causal observer estimates velocities from past positions,
(ii) a canonicalizer maps positions and estimated velocities to a phase state,
and (iii) the port-Hamiltonian core advances this phase state forward in time.

Formally, we observe...
```

### After (brief back-reference)
```latex
\subsection{Problem Formulation: Partial Observability (q-only)}
\label{sec:methods:qonly}

As described in Section~\ref{sec:intro}, PHAST operates in the q-only setting
where only generalized positions~$q_t$ are observed and momenta~$p_t$ are latent.
We now detail the three pipeline stages---velocity observer, canonicalizer, and
port-Hamiltonian core---that map a short position history to long-horizon
phase-space rollouts.

Formally, we observe...
```

**Key principle**: The reader shouldn't feel like the problem is being stated for the first time in Section 3. One sentence of back-reference + a roadmap of what *this section* adds is sufficient.

---

## Pattern 4: Concrete Instantiations for an Abstract Table

### Context
Table 1 lists systems with their $(V, M, D)$ decompositions, but entries like "$-g\cos\theta$" and "Scalar $m$" don't tell the reader *what these mean physically*.

### Implementation
Add after the interpretive-structure paragraph, before the figure:

```latex
\paragraph{Concrete instantiations.}
To make the mapping from physical system to $(V,\Mmat,\Dmat)$ template explicit,
we walk through three representative entries from
Table~\ref{tab:structured_hamiltonians}:
%
\begin{itemize}
\item \textbf{Simple pendulum} (KNOWN).
  State $q=\theta$ (angle), momentum $p=m\ell^2\dot\theta$ (angular momentum).
  The potential $V(\theta)=-mg\ell\cos\theta$ encodes gravity;
  mass $\Mmat=m\ell^2$ is a known scalar inertia;
  the only unknown is position-dependent air drag $\Dmat(\theta)$, which PHAST
  learns.
  Because both $V$ and $\Mmat$ are given, the inverse problem is fully
  identifiable.

\item \textbf{Cart-pole} (PARTIAL).
  State $q=(\text{cart position},\,\theta)$, a two-DOF system.
  Gravity gives $V(q)=mg\ell\cos\theta$ (template provided).
  The mass tensor $\Mmat(q)$ is a $2{\times}2$ configuration-dependent
  inertia coupling cart and pole (given from the Lagrangian or CAD model).
  Dissipation $\Dmat(q)$ has separate friction channels for the cart rail and
  pivot joint---learned with bounded strength.

\item \textbf{RLC circuit} (KNOWN, non-mechanical).
  State $q=q_C$ (charge on capacitor), momentum $p=Li$ (flux linkage, where
  $i$ is current and $L$ is inductance).
  Capacitive energy gives $V(q)=q^2/2C$; inductance plays the role of mass
  ($\Mmat=L$); resistance dissipates energy as heat ($\Dmat=R$).
  The same $(V,\Mmat,\Dmat)$ template applies, illustrating that the
  port-Hamiltonian decomposition extends beyond mechanics.
\end{itemize}
```

**Selection heuristic**:
1. **Fully known** (pendulum): Shows the simplest complete mapping
2. **Partially known** (cart-pole): Shows what "partial" means in practice (multi-DOF, mixed given/learned)
3. **Cross-domain** (RLC circuit): Surprises the reader by showing the same template works for non-mechanical systems

**Each entry answers**: What is the state? What is each component physically? What does the method learn vs. what's given?

---

## Pattern 5: Section Merging (Consolidation)

### Context
Sec 3.1 (Problem Formulation) and Sec 3.2 (Port-Hamiltonian Structure) both introduced the PH dynamics equation, creating redundancy.

### Protocol
1. **Move** unique content from 3.2 into 3.1 (passivity certificate, energy balance, forced dynamics stub)
2. **Delete** the subsection heading for 3.2
3. **Update the section roadmap** at the top of Sec 3:
   ```latex
   % Before: "...followed by the port-Hamiltonian structure (Sec 3.2),
   %          the parameterizations (Sec 3.3)..."
   % After:  "...followed by the parameterizations (Sec 3.2)..."
   ```
4. **Renumber** downstream subsection labels if needed
5. **Preserve** the old label as an alias if external refs exist:
   ```latex
   % Keep for backward compat if appendix references it:
   \label{sec:methods:ph}
   ```

---

## Pattern 6: Uncommenting Pedagogical Content

### Discovery
Papers often have extensive **commented-out explanations** that were removed for space. Before writing new exposition, always check for commented content:

```bash
# Find commented pedagogical content
grep -n "^%" methods.tex | grep -i "physical\|intuition\|meaning\|why\|because\|interpret"
```

### Workflow
1. Search for commented blocks near the section you're editing
2. Evaluate whether they address the reviewer's feedback
3. If yes, adapt (don't just uncomment — the style may need updating)
4. If no, write fresh content

**Real example**: The PHAST paper had 200+ lines of commented Energy-Casimir derivations with physical intuition. Instead of writing from scratch, we adapted the commented content.

---

---

## Pattern 7: Cross-Reference Connectivity Audit

### Context
After multiple rounds of restructuring (moving problem statement to intro, promoting content for arXiv, merging sections), the cross-reference graph can develop subtle inconsistencies that compile cleanly but confuse readers.

### Methodology
```bash
# 1. Map all labels and their locations
grep -rn '\\label{' *.tex | grep -v '^%'

# 2. Map all references
grep -rn '\\ref{' *.tex | grep -v '^%'

# 3. Find labels whose names don't match their location
# e.g., sec:methods:X defined in main_arxiv.tex (intro)
```

### Real Example: Mislocated Label
```latex
% In main_arxiv.tex (Introduction, Section 1):
\paragraph{Knowledge regimes.}
\label{sec:methods:regimes}   % <-- Name says "methods" but lives in intro!
```

Experiments.tex referenced it as `Sec.~\ref{sec:methods:regimes}`, which rendered as "Sec. 1" — confusing when readers expect Section 3.

**Fix**: Renamed to `sec:intro:regimes` across 4 files (main_arxiv.tex, experiments.tex, appendix.tex × 4 occurrences).

### Also Caught
- experiments.tex referenced `sec:methods:regimes` for the FD+TCN observer, but the observer is described in `sec:methods:qonly` — wrong target entirely

---

## Pattern 8: Table Claim Verification

### Context
Summary tables (e.g., "Identifiability: Yes/No/Partial") compress nuanced claims into single words. These must be verified against the detailed text.

### Methodology
For each cell in a claims column:
1. Find the detailed description (usually appendix or body text)
2. Check whether the claim is exact or qualified
3. If qualified, add a footnote in the table

### Real Example: N-body Identifiability
**Table said**: "Yes"
**Appendix said**: "jointly identifiable **up to an overall scale** (setting $G$ fixes the gauge)"

This is a genuine one-parameter gauge freedom ($m_i \to \alpha m_i$, $G \to G/\alpha$). The Lagrangian scales by $\alpha$, leaving equations of motion invariant.

**Fix**: Changed to `Yes$^\dagger$` with caption footnote explaining the G-fixes-gauge caveat.

### Notation Collision (Same Session)
The "General partially known" row had `$D_0 I + UU^\top$` in the **mass** column. Since $D$ is reserved for damping throughout the paper, this was confusing. Changed to `$m_0 I + UU^\top$`.

**Heuristic**: After filling in a table, read each column in isolation and check that every symbol is consistent with its column header's domain.

---

## Anti-Patterns to Avoid

### 1. Copy-Paste Between Sections
**Wrong**: Copy the problem statement into both Sec 1 and Sec 3.
**Right**: Write a summary for Sec 1, slim Sec 3 to back-reference.

### 2. Explaining Tables Inline in Captions
**Wrong**: Cramming concrete examples into a table caption.
**Right**: Keep caption concise; add a `\paragraph{Concrete instantiations.}` after the table.

### 3. Moving Content Without Checking References
**Wrong**: Move a `\label{eq:passivity}` to a new location without checking what `\ref{eq:passivity}` calls exist.
**Right**: Grep for all references before moving any labeled content.

### 4. Over-Slimming the Original Section
**Wrong**: Reducing Sec 3 to just "See Sec 1" — the reader needs the technical details here.
**Right**: One sentence of back-reference + roadmap of what this section *adds* beyond the intro.

### 5. Adding Concrete Examples That Don't Match the Table
**Wrong**: Explaining systems not in the table.
**Right**: Walk through actual table rows, using the same notation.

### 6. Label Names That Don't Match Their Location
**Wrong**: `\label{sec:methods:regimes}` defined inside the Introduction because it was "promoted from methods."
**Right**: Rename to `sec:intro:regimes` and update all references. Label names are documentation — they should tell you where to find the content.

### 7. Unqualified Claims in Summary Tables
**Wrong**: "Identifiable: Yes" when the detailed text says "up to an overall scale."
**Right**: "Yes$^\dagger$" with a caption footnote. Summary tables must not silently drop caveats.

### 8. Notation Reuse Across Domains
**Wrong**: Using $D_0$ for mass base diagonal when $D$ is the damping matrix.
**Right**: Use $m_0$ or $M_0$ for mass-related quantities. Each symbol family should be unambiguous within the paper.
