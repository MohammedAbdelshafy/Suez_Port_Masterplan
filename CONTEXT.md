---
type: repository
status: active
owner_repo: MohammedAbdelshafy/Suez_Port_Masterplan
product_name: Suez Port Masterplan
source_of_truth: https://github.com/MohammedAbdelshafy/Suez_Port_Masterplan
---

# Suez Port Masterplan CONTEXT

One job: generate consistent concept-level port layout drawings, quantities and reports from shared engineering inputs.

## Inputs
- Setup, assumptions and outputs: [README](README.md)
- Main configuration: [config.py](config.py)
- Generator: [generate_port.py](generate_port.py)
- Related CAD tool: [Coastal Structures Studio](https://github.com/MohammedAbdelshafy/suez-cad-generator)

## Process
1. Review the project requirements and the values in config.py.
2. Generate the port geometry and supporting tables.
3. Run the documented validation checks.
4. Review calculations, assumptions, standards and limits.
5. Export drawings and reports for academic/concept review.

## Output
A concept masterplan drawing and related views, quantities, coordinates and engineering report.

## Check
Run the documented validation and compare key dimensions to their inputs. Outputs are concept-level and not for construction; qualified maritime engineering review is required before any real project use.
