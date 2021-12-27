FROM odoo:15

USER root
# Mount Customize /mnt/"addons" folders for users addons
RUN mkdir -p /mnt/odoo

RUN mkdir -p /mnt/odoo \
    && mkdir -p /mnt/odoo/addons_external

COPY ./config/odoo.conf /etc/odoo/
COPY ./requirements.txt /mnt/odoo/
ADD ./addons /mnt/odoo/addons
ADD ./addons_external /mnt/odoo/addons_external
ADD ./data/ftp/odoo /mnt/odoo/data

RUN apt-get update && apt-get install -y --no-install-recommends \
        apt-utils \
        python3-dev \
        python3-wheel \
        chromium \
        ftp \
    && pip3 install --upgrade pip
RUN pip3 install -r /mnt/odoo/requirements.txt

RUN chown -R odoo /mnt/*

USER odoo
