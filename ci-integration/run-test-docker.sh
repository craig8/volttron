#!/usr/bin/env bash

source env/bin/activate

pytest -s -v "$@"