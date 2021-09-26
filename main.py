import pandas as pd
import random
import re


from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi_utils.timing import add_timing_middleware

# Parse the text output
RE = re.compile(
    "TIMING:\s+Wall:\s+(?P<wall>[\d\.]*)ms\s+\|\s+CPU:\s+(?P<cpu>[\d\.]*)ms\s+\|\s+main\.(?P<name>\w*)"
).match

results = []


def record(message: str) -> None:
    """
    Test function to overwrite the default record of basic instrumentation
    """
    global results
    res = RE(message)
    results.append(res.groupdict())
    # TODO: Instead of printing, we'll send the aggregated results to Prometheus (maybe)
    print(results)


app = FastAPI()
add_timing_middleware(app, record=record)

df = None


@app.on_event("startup")  # Run when API starts
@repeat_every(seconds=300)  # then run every 5min
def generate_numbers() -> None:
    global df
    # Generated a random pandas Series for testing
    l = [random.randint(2, 5) for i in range(random.randint(1000000, 10000000))]
    df = pd.DataFrame({"value": l})


@app.get("/items/")
async def get_items() -> dict:
    desc = df.value
    return {
        "total": len(desc),
        "min": int(desc.min()),
        "max": int(desc.max()),
        "variance": float(desc.std()),
    }
