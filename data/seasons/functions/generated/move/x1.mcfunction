scoreboard players set branch_x_1 _seasons 0
execute if score x _seasons matches ..-1 run scoreboard players set branch_x_1 _seasons -1
execute if score x _seasons matches 1.. run scoreboard players set branch_x_1 _seasons 1

execute if score branch_x_1 _seasons matches -1 run scoreboard players add x _seasons 1
execute if score branch_x_1 _seasons matches 1 run scoreboard players remove x _seasons 1

execute if score branch_x_1 _seasons matches -1 positioned ~-1 ~ ~ run tp @s ~ ~ ~
execute if score branch_x_1 _seasons matches 0 run tp @s ~ ~ ~
execute if score branch_x_1 _seasons matches 1 positioned ~1 ~ ~ run tp @s ~ ~ ~
scoreboard players reset branch_x_1 _seasons