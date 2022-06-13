FROM nginx:1.21.6-alpine

VOLUME container_folder

RUN --mount type=volume,src=./host_dir,dst=./container_folder
