# camp2docker
Utility to transform a CAMP plan into Docker and fig files

## CAMP

[CAMP](https://www.oasis-open.org/committees/camp/) is a standard from OASIS defining a standardised interface and application description model ([CAMP PDP](http://docs.oasis-open.org/camp/camp-spec/v1.1/csprd02/camp-spec-v1.1-csprd02.html#_Toc380683863))

## Development environment

Use [virtualenv](http://virtualenv.readthedocs.org/en/latest/) to created an isolated development environment:
`virtualenv env`

Install dependencies with [pip](http://pip.readthedocs.org/en/latest/):
`pip install requirements.txt`

## Docker
You can build directly the Docker image from this repository with `docker build git@github.com:thlacroix/camp2docker.git`

## Configuration
The configuration files are in the [config](config) directory.

## CLI

Run the CLI with:

`python camp2docker.py process <planfile>` to show the result in the terminal

`python camp2docker.py generate <planfile> <output_folder>` to generate the files in `<output_folder>`

## Test
Use `nosetest tests/unit` on the root directory to run all the tests

## License
[MIT](LICENSE)
