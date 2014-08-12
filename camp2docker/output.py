import pystache

class InstructionError(Exception):
    pass

class Container(object):
    def  __init__(self, name, base):
        self.name = name
        self.base = base
        self.instructions = []

        self.cmd = None
        self.entrypoint = None

        self.volumes = []
        self.links = []
        self.exposes = []

    @classmethod
    def from_service(cls, service):
        return cls(service.name, service.base)

    @staticmethod
    def process_mustache_template_list(instruction, params):
        return [pystache.render(elem, params) if type(elem) is str else elem for elem in instruction ]

    def process_instructions(self, instructions, params, source_container):
        for instruction in instructions:
            instruction = self.process_mustache_template_list(instruction, params)
            if not instruction[1]:
                continue
            if instruction[0] == 'VOLUME':
                self.add_instruction(instruction)
                self.add_volume(instruction[1:], source_container)
            elif instruction[0] == 'LINK':
                self.add_link(instruction[1], source_container)
            elif instruction[0] == 'EXPOSE':
                self.add_expose(instruction[1])
            elif instruction[0] == 'CMD':
                if self.cmd is None:
                    self.cmd = instruction[1]
                else:
                    raise InstructionError("Two CMD")
            elif instruction[0] == 'ENTRYPOINT':
                if self.entrypoint is None:
                    self.entrypoint = instruction[1]
                else:
                    raise InstructionError("Two ENTRYPOINT")
            else:
                self.add_instruction(instruction)

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def add_expose(self, expose):
        self.exposes.append(expose)

    def add_link(self, link, source_container):
        if link.has_key('self') and link["self"] == True:
            self.links.append(source_container)
        else:
            self.links.append(link)

    def add_volume(self, volume, source_container):
        self.volumes.append(volume)

    @property
    def needs_build(self):
        for i in self.instructions:
            if i[0] in ["RUN", "ADD"]:
                return True
        return False

    def __repr__(self):
        res = "# {filename}".format(filename=self.name)
        for link in self.links:
            res += " -> {container_name}".format(container_name=link.name)
        res+= "\nFROM {base_image}\n".format(base_image=self.base)
        for instruction in self.instructions:
            res+= "{INSTRUCTION_TYPE} {instruction_parameter}\n".format(INSTRUCTION_TYPE=instruction[0], instruction_parameter=instruction[1])
        if self.cmd is not None:
            res+= "CMD {command}\n".format(command=self.cmd)
        if self.entrypoint is not None:
            res += "ENTRYPOINT {entrypoint}\n".format(entrypoint=self.entrypoint)
        if len(self.exposes) >0:
            res+= 'EXPOSE {ports}\n'.format(ports=' ,'.join(self.exposes))
        return res

class Fig(object):
    def __init__(self, project_name):
        self.name = project_name


class Fleet(object):
    pass
