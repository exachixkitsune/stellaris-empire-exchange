#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: nospell ts=4 expandtab

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

import glob
import json
import http.server

import clauswitz
import importer


EmpireData = TypedDict(
    "EmpireData", {"author": str, "name": str, "ethics": List[str], "bio": str}
)


def page_ajax_list(self: http.server.BaseHTTPRequestHandler, folder: str) -> None:
    """Sends an AJAX fragment listing available files in a folder"""

    # Get the list of files that are in the file.
    files = glob.glob(f"{folder}/**/*.txt")
    output: List[EmpireData] = []

    for filename in files:
        # Parse the Empire in the file.
        with open(filename, "r") as handle:
            obj = clauswitz.parse_data(handle)

        # Extract the empire data out of the wrapper object.
        if isinstance(obj, list) and len(obj) == 1:
            if isinstance(obj[0], tuple):
                obj = obj[0][1]

        # Get the fields we want in the fragment.
        name = str(importer.get_value(obj, "key"))
        author = str(importer.get_value(obj, "author"))
        ethics = importer.get_values(obj, "ethic")

        bio = ""
        species = importer.get_value(obj, "species")
        if isinstance(species, list):
            bio = str(importer.get_value(species, "species_bio"))

        # Make the ethics presentable.
        ethics_out = [
            str(ethic).replace("ethic_", "").replace("_", " ") for ethic in ethics
        ]

        # Add to the output list
        output.append(EmpireData(author=author, name=name, ethics=ethics_out, bio=bio))

    # Convert the list to JSON for JS client.
    json_data = json.dumps(output).encode("utf-8")

    # Send the response
    self.send_response(200)
    self.send_header("Content-Type", "text/json")
    self.send_header("Content-Length", str(len(json_data)))
    self.end_headers()

    self.wfile.write(json_data)
