#!/bin/bash

setup_user() {
    echo "Starting with UID : ${NB_UID}, GID: ${NB_GID}"
    usermod -u ${NB_UID} user
    groupmod -g ${NB_GID} usergroup

    if [[ "${GRANT_SUDO}" == "1" || "${GRANT_SUDO}" == 'yes' ]]; then
        echo "Granting user sudo access"
        echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/usergroup
    fi
}

run_as_user() {
    su - user -c "conda activate myenv; $*"
}


main() {
    setup_user
    run_as_user "$@"
}

main "$@"

