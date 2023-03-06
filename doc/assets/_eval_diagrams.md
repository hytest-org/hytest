
# Model Eval Block Diagram

This is the `mermaid` source used to generate the various model eval diagrams in the `doc/assets` folder. 
This code can be intepreted with markdown or other interpreter, if the documentation system supports
such extensions.  

In our case, we used the online generator at <https://mermaid.live/> to render this code, and the SVG included
in various notebooks across the repo. 


```mermaid
    flowchart LR
        classDef thisStep fill:#ff0,stroke:#333,stroke-width:2px;
            SIM[(Simulated /<br>Modeled)]
            OBS[(Observed /<br>Reference)]

        subgraph PreProc [Data Preparation]
            direction TB
            SIM_r[[Simulated<br>/<br>Modeled<br>]]
            OBS_r[[Observed<br>/<br>Reference]]
        end
        subgraph Analysis
            direction LR
            Metrics[/Metrics/]
            Domain[/Domain/]
            Data[("Data")]
            Analysis_r[[<font size=6>Analysis]]
            Domain --> Analysis_r
            Data --> Analysis_r
            Metrics --> Analysis_r
        end
        subgraph Viz [Visualization]
            direction TB
            Explore
            Plot
            Score
            Explore-.->Plot-.->Score
        end
        SIM --> SIM_r
        OBS --> OBS_r
        SIM_r --> Data
        OBS_r --> Data
        Analysis_r --"Metrics"--> Viz

        %% change 'Src' to the node name you want to highlight
        %% Src | PreProc | Analysis | Viz
        %%class Src thisStep
```
