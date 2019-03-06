#!/bin/bash
function lssh(){
    params=$*
    local names=()
    IFS=$'
'
    for line in $( aws-gate list  );
    do
        if [ $# -eq 0 ];then
            names+=( ${line}  )
        else
            if [ "$line" != "${line/$params/}" ]; then
                names+=( ${line}  )
            fi
        fi
    done
    COUNTER=0
    menu names[@]

}
function menu(){
    declare -a local options=("${!1}")
    re='^[0-9]+$'
    select name in ${options[@]}; do
        if [[ $REPLY =~ $re ]]; then
                    aws-gate session ${name%% *} ; exit
        else
             filter  options[@]  $REPLY
             break
        fi
    done


}
lssh
