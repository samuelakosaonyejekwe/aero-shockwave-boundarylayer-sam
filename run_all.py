"""
MASTER PIPELINE RUNNER  -  UniSTAR-CFD SWBLI/transition case study
Runs every stage in order and rebuilds case.docx + dwg.docx.
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import runpy, os
HERE = os.path.dirname(os.path.abspath(__file__))

STAGES = [
    "01_geometry/build_geometry.py",
    "02_mesh/build_mesh.py",
    "03_model_setup/build_setup.py",
    "04_solution/run_solver.py",
    "04_solution/engineering_outputs.py",
    "06_validation/validate.py",
    "01_geometry/engineering_drawings.py",
    "07_3D_solution/run_3d.py",
    "05_postprocessing/postprocess.py",   # after 07 so tables() can consolidate the 3-D spanwise table
    "build_docx.py",
]

if __name__ == "__main__":
    for s in STAGES:
        print(f"\n===== RUN {s} =====")
        runpy.run_path(os.path.join(HERE, s), run_name="__main__")
    print("\nAll stages complete -> case.docx, dwg.docx")
