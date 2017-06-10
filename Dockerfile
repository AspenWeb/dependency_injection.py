FROM funkyfuture/nest-of-serpents

ARG uid

ENTRYPOINT tox
WORKDIR /src

RUN pip3.6 install flake8 pytest tox Sphinx \
 && mkdir /home/tox \
 && mv /root/.cache /home/tox/ \
 && useradd --uid=$uid -m tox \
 && chown -R tox.tox /home/tox/.cache

ADD . .
RUN chown -R tox.tox .

USER tox
