# make a link to wherever bash is on this machine
rm /tmp/meerkat/installer.run /tmp/meerkat/bash 2> /dev/null

set -e

mkdir -p /tmp/meerkat/

set +e

RUN_OPT=""

if [ -n "$GPU" ] ; then
    echo "Using gpus: "$GPU
    RUN_OPT="GPU=$GPU"
else
    echo "Not using gpus"
fi

if [ -n "$MOVIDIUS" ] ; then
    RUN_OPT=$RUN_OPT" MOVIDIUS=${MOVIDIUS}"
fi

if [ -n "${NUM_DESCRIPTOR_WORKERS}" ] ; then
    echo "Using the following descriptor workers: "$NUM_DESCRIPTOR_WORKERS
    RUN_DESCRIPTOR="NUM_DESCRIPTOR_WORKERS=${NUM_DESCRIPTOR_WORKERS}"
else
    echo "Don't specifying descriptor server workers"
fi

if [ -n "$NET" ] ; then
    RUN_OPT=$RUN_OPT" NETWORK=${NET}"
fi

if [ -n "${NUM_WORKERS}" ] ; then
    RUN_OPT=$RUN_OPT" NUM_WORKERS=${NUM_WORKERS}"
fi

RUN_OPT=$RUN_OPT" $(env | grep -e '^DNS=' -e '^SSL_CERTS=' | tr '\n' ' ')"
RUN_OPT=$RUN_OPT" $(env | grep -e '^MEERKAT_' | tr '\n' ' ')"

ln -sf $(which bash) /tmp/meerkat/bash
sudo chmod a+x installer.run
sudo /tmp/meerkat/bash -c "$RUN_OPT $RUN_DESCRIPTOR ./installer.run"

if [ $? -ne 0 ]; then
    echo " "
    echo "======================================================================"
    echo "                    INSTALLATION ERROR "
    echo "Errors were logged to /tmp/meerkat/frapi.log "
    echo "Showing last 20 lines: "
    echo "======================================================================"
    echo " "
    tail -n20 /tmp/meerkat/frapi.log
    exit 1
fi
