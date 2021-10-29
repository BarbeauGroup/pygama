#!/bin/bash
#
# With `env` distributions that implement the -S flag, it is possible to
# directly run the script inside the container with the following shebang:
#
#!/usr/bin/env -S singularity exec /data1/shared/lar-commissioning/software/containers/legend-container.sif bash

root_dir="/data1/shared/lar-commissioning"
prod_base="$root_dir/data/pgt"
run_name="run0028-mid-june-sipm-test"
meta_path="$root_dir/software/meta/pgt/$run_name"
fcio_files="$prod_base/daq/$run_name/.*\.fcio"
local_sw="$root_dir/software/pygama-v01"

export PYTHONUSERBASE="$root_dir/software/pygama-v01/local"

"$local_sw/pygama-run.py" \
    --verbose \
    --step daq_to_raw \
    --input-files "$fcio_files" \
    --output-dir "$prod_base/raw/$run_name" \
    --config-file "$meta_path/d2r_config.json" # --overwrite

"$local_sw/pygama-run.py" \
    --verbose \
    --step raw_to_dsp \
    --input-files "$prod_base/raw/$run_name/.*\.lh5" \
    --output-dir "$prod_base/dsp/$run_name" \
    --config-file "$meta_path/r2d_config.json" # --overwrite
