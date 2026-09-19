import pandas as pd

 

from engine.simulator import run_simulation

 

results = run_simulation()

 

output = pd.DataFrame(results)

 

output.to_csv(

    "output/simulation_outputs.csv",

    index=False

)

 

print(output)