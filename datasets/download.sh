#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

read -p "Enter global data path : " DIR 
read -p "Enter model : " Model

#editing path in config file
PATH_FORMAT=${DIR////\\/}
sed -i "s/datafile.*$/datafile : \"${PATH_FORMAT}\"/" ../configs/${Model}.yml


Help()
{
    echo "-f    Download femnist dataset for Federated Learning Experiments"
}

femnist()
{
    if [ ! -d "${DIR}/femnist/client_data_mapping/" ]; 
    then
        echo "Downloading femnist dataset..."   
        wget -O ${DIR}/femnist.tar.gz https://fedscale.eecs.umich.edu/dataset/femnist.tar.gz
        
        echo "Dataset downloaded, now decompressing..." 
        tar -xf ${DIR}/femnist.tar.gz -C ${DIR}

        echo "Removing compressed file..."
        rm -f ${DIR}/femnist.tar.gz

        echo -e "${GREEN}femnist dataset downloaded!${NC}"
    else
        echo -e "${RED}femnist dataset already exists under ${DIR}/femnist/!"
fi
}
while getopts ":hsoacegildrtwfxo" option; do
   case $option in
      h ) # display Help
         Help
         exit;;
      f )
         femnist
         ;;           
      \? ) 
         echo -e "${RED}Usage: cmd [-h] [-A] [-o] [-t] [-p]${NC}"
         exit 1;;
   esac
done

if [ $OPTIND -eq 1 ]; then 
    echo -e "${RED}Usage: cmd [-h] [-A] [-o] [-t] [-p]${NC}"; 
fi
