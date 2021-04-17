FROM public.ecr.aws/lambda/python:3.7


# Install ffmpeg
RUN curl https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz -s
RUN tar -xf ffmpeg.tar.xz
RUN mv ffmpeg-4.4-amd64-static/ffmpeg /usr/bin


COPY app.py   ./
CMD ["app.handler"]
