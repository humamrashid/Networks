#!/bin/bash -x
# Humam Rashid
# CISC 7334X, Prof. Chen

#vms=(Bushwick EastNY Flatbush Midwood)
#for vm in "${vms[@]}"; do
    #vboxmanage controlvm ${vm} poweroff
#done

# Diamond Ethernets
# DiamondMidwoodFlatbush (3 - 3)
vboxmanage modifyvm Midwood --nic3 intnet 
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Midwood --intnet3 "DiamondMidwoodFlatbush"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Flatbush --nic3 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Flatbush --intnet3 "DiamondMidwoodFlatbush"
[ $? -eq 0 ] || exit $?

# DiamondMidwoodBushwick (4 - 3)
vboxmanage modifyvm Midwood --nic4 intnet 
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Midwood --intnet4 "DiamondMidwoodBushwick"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Bushwick --nic3 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Bushwick --intnet3 "DiamondMidwoodBushwick"
[ $? -eq 0 ] || exit $?
# DiamondFlatbushEastNY (4 - 3)
vboxmanage modifyvm Flatbush --nic4 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Flatbush --intnet4 "DiamondFlatbushEastNY"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm EastNY --nic3 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm EastNY --intnet3 "DiamondFlatbushEastNY"
[ $? -eq 0 ] || exit $?
# DiamondBushwickEastNY (4 - 4)
vboxmanage modifyvm Bushwick --nic4 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Bushwick --intnet4 "DiamondBushwickEastNY"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm EastNY --nic4 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm EastNY --intnet4 "DiamondBushwickEastNY"
[ $? -eq 0 ] || exit $?


# Line Ethernets
# LineMidwoodFlatbush (5 - 5)
vboxmanage modifyvm Midwood --nic5 intnet 
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Midwood --intnet5 "LineMidwoodFlatbush"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Flatbush --nic5 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Flatbush --intnet5 "LineMidwoodFlatbush"
[ $? -eq 0 ] || exit $?
# LineFlatbushBushwick (6 - 5)
vboxmanage modifyvm Flatbush --nic6 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Flatbush --intnet6 "LineFlatbushBushwick"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Bushwick --nic5 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Bushwick --intnet5 "LineFlatbushBushwick"
[ $? -eq 0 ] || exit $?
# LineBushwickEastNY (6 - 5)
vboxmanage modifyvm Bushwick --nic6 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm Bushwick --intnet6 "LineBushwickEastNY"
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm EastNY --nic5 intnet
[ $? -eq 0 ] || exit $?
vboxmanage modifyvm EastNY --intnet5 "LineBushwickEastNY"
[ $? -eq 0 ] || exit $?

#for vm in "${vms[@]}"; do
    #vboxmanage startvm ${vm} --type headless
#done

# EOF.
