#!/bin/bash

pgrep redis | xargs kill
pgrep redis-sentinel | xargs kill
