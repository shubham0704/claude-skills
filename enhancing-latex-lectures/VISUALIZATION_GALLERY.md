# Visualization Code Gallery

Quick-reference templates for common visualization patterns. Copy-paste and adapt.

## Color Schemes

```latex
% Perceptually uniform (preferred)
colormap/viridis  % Blue-green-yellow
colormap/plasma   % Purple-pink-yellow
colormap/inferno  % Black-red-yellow

% Diverging
colormap/cool     % Cyan-magenta
colormap/hot      % Black-red-yellow-white

% For heatmaps
colormap/jet      % Rainbow (use sparingly - not perceptually uniform)
```

## Template 1: 3D Surface Plot

```latex
\begin{axis}[
    width=6cm, height=5cm,
    xlabel={$x$},
    ylabel={$y$},
    zlabel={$f(x,y)$},
    colormap/viridis,
    view={120}{30},  % azimuth, elevation
    colorbar,
    colorbar style={ylabel={Value}},
]
\addplot3[
    surf,
    shader=interp,
    samples=30,
    domain=-2:2,
    y domain=-2:2,
] {x^2 + y^2};  % Your function here
\end{axis}
```

## Template 2: 2D Heatmap (Top-Down View)

```latex
\begin{axis}[
    width=6cm, height=6cm,
    xlabel={$x$},
    ylabel={$y$},
    colormap/viridis,
    view={0}{90},  % Top-down
    colorbar,
    xmin=0, xmax=10,
    ymin=0, ymax=10,
]
\addplot3[
    surf,
    shader=interp,
    samples=30,
    domain=0:10,
    y domain=0:10,
] {sqrt((x-5)^2 + (y-5)^2)};

% Optional: Add markers
\node[circle, fill=white, draw=black, thick, inner sep=2pt]
  at (axis cs:5, 5, 0) {G};
\end{axis}
```

## Template 3: Line Plot with Multiple Series

```latex
\begin{axis}[
    width=8cm, height=6cm,
    xlabel={Iteration},
    ylabel={Cost},
    grid=major,
    legend pos=north east,
    xmin=0, xmax=100,
]
% Series 1
\addplot[thick, blue, mark=*, mark repeat=5] coordinates {
    (0,100) (10,80) (20,60) (30,40) (40,20) (50,10)
};
\addlegendentry{Method 1}

% Series 2
\addplot[thick, red, mark=square*, mark repeat=5] coordinates {
    (0,100) (20,80) (40,60) (60,40) (80,20) (100,10)
};
\addlegendentry{Method 2}

% Threshold line
\draw[dashed, black, thick] (axis cs:0,15) -- (axis cs:100,15)
  node[right] {threshold};
\end{axis}
```

## Template 4: Logarithmic Scale (Convergence Plot)

```latex
\begin{axis}[
    width=8cm, height=6cm,
    xlabel={Iteration},
    ylabel={Error},
    ymode=log,  % Logarithmic y-axis
    grid=major,
    legend pos=north east,
    ymin=0.001, ymax=10,
]
\addplot[thick, blue, mark=*] coordinates {
    (0,10) (10,1) (20,0.1) (30,0.01) (40,0.001)
};
\addlegendentry{Exponential convergence}
\end{axis}
```

## Template 5: Scatter Plot with Regression

```latex
\begin{axis}[
    width=7cm, height=6cm,
    xlabel={MDP Cost-to-go},
    ylabel={LMDP Cost-to-go},
    grid=major,
    xmin=0, xmax=10,
    ymin=0, ymax=10,
]
% Scatter points
\addplot[only marks, mark=*, blue!60, opacity=0.6] coordinates {
    (1,1.02) (2,2.01) (3,3.03) (4,3.98) (5,5.05)
    (6,5.97) (7,7.04) (8,8.02) (9,9.01)
};

% Perfect correlation line
\addplot[thick, red, dashed, domain=0:10] {x};
\node[right, red] at (axis cs:8,8) {$y=x$};

% Best fit line
\addplot[thick, green!60!black, domain=0:10] {1.01*x - 0.05};
\node[right, green!60!black] at (axis cs:7,7.5) {$R^2=0.986$};
\end{axis}
```

## Template 6: Three-Panel Comparison

```latex
\begin{tikzpicture}[scale=1.0]

% Panel 1
\begin{scope}[shift={(0,0)}]
\node[above, font=\large\bfseries] at (3, 4.8) {Panel 1 Title};
\begin{axis}[width=5.5cm, height=5cm, ...]
  % Your plot
\end{axis}
\end{scope}

% Panel 2 (shift right by width + gap)
\begin{scope}[shift={(6.5,0)}]
\node[above, font=\large\bfseries] at (3, 4.8) {Panel 2 Title};
\begin{axis}[width=5.5cm, height=5cm, ...]
  % Your plot
\end{axis}
\end{scope}

% Panel 3
\begin{scope}[shift={(13,0)}]
\node[above, font=\large\bfseries] at (3, 4.8) {Panel 3 Title};
\begin{axis}[width=5.5cm, height=5cm, ...]
  % Your plot
\end{axis}
\end{scope}

\end{tikzpicture}
```

## Template 7: Six-Panel Grid (2×3)

```latex
\begin{tikzpicture}[scale=1.0]

% TOP ROW
\begin{scope}[shift={(0,6)}]  % Top-left
  % Panel 1
\end{scope}

\begin{scope}[shift={(5.5,6)}]  % Top-middle
  % Panel 2
\end{scope}

\begin{scope}[shift={(11,6)}]  % Top-right
  % Panel 3
\end{scope}

% BOTTOM ROW
\begin{scope}[shift={(0,0)}]  % Bottom-left
  % Panel 4
\end{scope}

\begin{scope}[shift={(5.5,0)}]  % Bottom-middle
  % Panel 5
\end{scope}

\begin{scope}[shift={(11,0)}]  % Bottom-right
  % Panel 6
\end{scope}

\end{tikzpicture}
```

## Template 8: Quiver Plot (Vector Field)

```latex
\begin{axis}[
    width=6cm, height=6cm,
    xlabel={$x$},
    ylabel={$y$},
    xmin=-2, xmax=2,
    ymin=-2, ymax=2,
    axis equal,
]
% Background heatmap (optional)
\addplot3[surf, shader=interp, samples=20,
          domain=-2:2, y domain=-2:2, opacity=0.3]
  {x^2 + y^2};

% Vector field
\addplot[blue!70, quiver={u={-x}, v={-y},
         scale arrows=0.2}]
  coordinates {
    (-2,-2) (-1,-2) (0,-2) (1,-2) (2,-2)
    (-2,-1) (-1,-1) (0,-1) (1,-1) (2,-1)
    (-2,0)  (-1,0)  (0,0)  (1,0)  (2,0)
    (-2,1)  (-1,1)  (0,1)  (1,1)  (2,1)
    (-2,2)  (-1,2)  (0,2)  (1,2)  (2,2)
  };
\end{axis}
```

## Template 9: Contour Plot

```latex
\begin{axis}[
    width=7cm, height=7cm,
    xlabel={$x$},
    ylabel={$y$},
    colormap/viridis,
    view={0}{90},
]
\addplot3[
    contour gnuplot={
        levels={1,2,3,4,5},
        labels=false,
    },
    thick,
] {x^2 + y^2};

% Filled contours
\addplot3[
    contour filled={number=10},
    opacity=0.5,
] {x^2 + y^2};
\end{axis}
```

## Template 10: Insight Box

```latex
% Blue box - Theorems/Definitions
\begin{tcolorbox}[colback=blue!5,colframe=blue!75!black,
  title={\textbf{THEOREM: Name}},sharp corners,enhanced]
Content here.
\end{tcolorbox}

% Green box - Results/Findings
\begin{tcolorbox}[colback=green!5,colframe=green!60!black,
  title={\textbf{KEY FINDING: Name}},sharp corners,enhanced]
Content here.
\end{tcolorbox}

% Purple box - Insights/Interpretations
\begin{tcolorbox}[colback=purple!5,colframe=purple!70!black,
  title={\textbf{WHY THIS MATTERS}},sharp corners,enhanced]
Content here.
\end{tcolorbox}

% Orange box - Algorithms/Procedures
\begin{tcolorbox}[colback=orange!5,colframe=orange!70!black,
  title={\textbf{ALGORITHM: Name}},sharp corners,enhanced]
Content here.
\end{tcolorbox}

% Red box - Warnings/Pitfalls
\begin{tcolorbox}[colback=red!5,colframe=red!75!black,
  title={\textbf{COMMON PITFALL: Name}},sharp corners,enhanced]
Content here.
\end{tcolorbox}
```

## Template 11: Comparison Table

```latex
\begin{center}
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Method} & \textbf{Complexity} & \textbf{Accuracy} & \textbf{Speed} \\
\hline
Method 1 & $O(n^2)$ & 95\% & 1× \\
Method 2 & $O(n^3)$ & 99\% & 0.1× \\
\textbf{LMDP (ours)} & $O(n^3)$ & 99\% & \textbf{10×} \\
\hline
\end{tabular}
\end{center}
```

## Template 12: Side-by-Side Heatmaps

```latex
\begin{tikzpicture}[scale=1.0]

% Left heatmap
\begin{scope}[shift={(0,0)}]
\node[above, font=\large\bfseries] at (4, 6.3) {Method 1};
\begin{axis}[
    width=7cm, height=6cm,
    colormap/viridis,
    view={0}{90},
    colorbar,
]
\addplot3[surf, shader=interp, samples=30,
          domain=0:10, y domain=0:10]
  {sin(deg(x))*cos(deg(y))};
\end{axis}
\end{scope}

% Right heatmap
\begin{scope}[shift={(9,0)}]
\node[above, font=\large\bfseries] at (4, 6.3) {Method 2};
\begin{axis}[
    width=7cm, height=6cm,
    colormap/viridis,
    view={0}{90},
    colorbar,
]
\addplot3[surf, shader=interp, samples=30,
          domain=0:10, y domain=0:10]
  {sin(deg(x))*cos(deg(y)) + 0.1*x};
\end{axis}
\end{scope}

\end{tikzpicture}
```

## Template 13: Parametric Functions

```latex
\begin{axis}[
    width=6cm, height=6cm,
    xlabel={$x$},
    ylabel={$y$},
    axis equal,
]
% Parametric curve
\addplot[thick, blue, domain=0:2*pi, samples=100]
  ({cos(deg(x))}, {sin(deg(x))});

% With variable radius
\addplot[thick, red, domain=0:4*pi, samples=200]
  ({(1 + 0.5*cos(5*deg(x)))*cos(deg(x))},
   {(1 + 0.5*cos(5*deg(x)))*sin(deg(x))});
\end{axis}
```

## Quick Tips

### Spacing in Multi-Panel Figures
```latex
% For 3 panels side-by-side (width 5.5cm each):
shift={(0,0)}      % Left
shift={(6.5,0)}    % Middle (5.5 + 1.0 gap)
shift={(13,0)}     % Right (6.5 + 6.5)

% For 2×3 grid:
% Top row: y-shift = 6
% Bottom row: y-shift = 0
% Columns: x-shift = 0, 5.5, 11
```

### Font Sizes
```latex
\node[font=\tiny] {text};        % Smallest
\node[font=\footnotesize] {text};
\node[font=\small] {text};
\node[font=\normalsize] {text};  % Default
\node[font=\large] {text};
\node[font=\Large] {text};
\node[font=\LARGE] {text};
\node[font=\huge] {text};        % Largest
```

### Mark Styles
```latex
mark=*            % Filled circle
mark=o            % Empty circle
mark=square*      % Filled square
mark=square       % Empty square
mark=triangle*    % Filled triangle
mark=diamond*     % Filled diamond
mark=x            % Cross
mark=+            % Plus
```

### Line Styles
```latex
thick             % Thick line
ultra thick       % Very thick
dashed            % Dashed line
dotted            % Dotted line
dash pattern=on 2pt off 3pt  % Custom pattern
opacity=0.5       % Semi-transparent
```

### Common Math Functions
```latex
% In \addplot expressions:
sin(deg(x))       % Sine (deg converts radians to degrees)
cos(deg(x))       % Cosine
exp(x)            % e^x
ln(x)             % Natural log
sqrt(x)           % Square root
abs(x)            % Absolute value
x^2               % Power
```

### Conditional Expressions
```latex
% Ternary operator: condition ? value_if_true : value_if_false
{x > 0 ? x^2 : -x^2}
{x > 0.01 && y > 0.01 ? ln(x*y) : 0}  % Avoid log(0)
```
