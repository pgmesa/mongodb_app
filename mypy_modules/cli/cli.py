
from .aux_classes import Command, Flag
from .cli_utils import format_str

from .external_dep import colorama
from .external_dep.colorama import Fore, Back, Style

class Cli:
    """Interfaz que se encarga de controlar que la linea de comandos
    introducida en un programa es correcta, (mira que todos los flags y 
    comandos introducidos por terminal son correctos y compatibles).
    Hace falta una configuracion previa (definir que comandos y flags
    que va a tener el programa y sus caracteristicas)"""
    def __init__(self, main_cmd:Command, 
                            def_basic_help=True, def_advanced_help=False):
        self.main_cmd = main_cmd
        self.global_flags = {}
        if def_basic_help:
            h = Flag("-h",
                    description=("shows overall information about a command or " + 
                                "all of them if a valid one is not introduced"),
                )
            self.global_flags[h.name] = h
        if def_advanced_help:
            hc = Flag("-hc",
                description=("is the same as -h but with some predefined " + 
                            "colors"),
                notcompat_withflags=["-h"]
            )
            self.global_flags[hc.name] = hc
            ha = Flag("-ha",
                    description=("is the same as -h but displaying all information"),
                    notcompat_withflags=["-h", "-hc"]
                )
            self.global_flags[ha.name] = ha
            hca = Flag("-hca",
                    description=("combines -h, -hc and -ha"),
                    notcompat_withflags=["-h", "hc", "ha"]
                )
            self.global_flags[hca.name] = hca
            
    
    def add_global_flag(self, flag:Flag):
        """Añade un flag accesible por todos los comandos y subcomandos

        Args:
            flag (Flag): Flag a añadir
        """
        self.global_flags[flag.name] = flag
        
    def process_cmdline(self, args:list) -> dict:
        """Procesa los argumentos que se pasan como parametro. Informa 
        de si estos son validos o no en base a los comandos y flags 
        que conformen la cli.

        Args:
            args (list): Linea de comandos a procesar

        Raises:
            CmdLineError: Si no se han proporcionado argumentos
            CmdLineError: Si el comando no es correcto

        Returns:
            dict: diccionario con el comando, las opciones del comando
                y los flags como claves y los parametros que se les 
                hayan pasado como valores (si esque se les ha pasado
                alguno)
        """
        processed_line = {}
        if self.main_cmd.name == args.pop(0):
            processed_line = self._process_cmd(self.main_cmd, args)
        else:
            raise CmdLineError(" El comando main introducido es incorrecto")
        return processed_line
    
    def _process_cmd(self, cmd:Command, args:list):
        processed_line = { 
            "args": [], "options": {}, "flags": [], "nested_cmds": {},
        }
        params, options, nested_cmds = self._split_line(cmd, args)
        # Procesamos flags del comando
        flags = self._check_flags(params, cmd=cmd)
        processed_line["flags"] = flags
        # Procesamos parametros del comando
        params = self._check_valid_params(cmd, params)
        processed_line["args"] = params
        # Procesamos las opciones del comando
        for opt_name, opt_params in options.items():
            opt = cmd.options[opt_name]
            opt_params = self._check_valid_params(opt, opt_params)
            processed_line["options"][opt_name] = opt_params
        # Procesamos los comandos anidados de forma recursiva
        if len(nested_cmds) == 0 and cmd.mnc:
            err = (f"El comando '{cmd.name}' requiere un comando extra "
                   f"-> {list(cmd.nested_cmds.keys())}")
            raise CmdLineError(err)
        for cmd_name, nested_args in nested_cmds.items():
            nested_cmds = cmd.nested_cmds[cmd_name]
           
            processed_line["nested_cmds"][cmd_name] = (
                self._process_cmd(nested_cmds, nested_args)
            )
        return processed_line
    
    def _split_line(self, cmd:Command, args:list) -> dict:
        # Separamos por partes la linea de comandos
        ant = None; last_index = 1
        params = []; opts = {}; nested_cmds = {} 
        for i, arg in enumerate(args):
            if arg in cmd.nested_cmds:
                if ant is not None:
                    opts[ant] = args[last_index:i]
                nested_cmds[arg] = args[i+1:]
                break
            elif arg in cmd.options:
                if arg in opts or arg == ant:
                    msg = f"La opcion '{ant}' esta repetida"
                    raise CmdLineError(msg)
                if ant is not None:
                    opts[ant] = args[last_index:i]
                last_index = i + 1
                ant = arg 
            elif ant is None:
                params.append(arg) 
        else:
            if ant is not None:
                opts[ant] = args[last_index:]
        return params, opts, nested_cmds
      
    def _check_valid_params(self, cmd:Command, params:list) -> list:
        """Revisa si los parametro que se han pasado a un comando 
        (puede ser una opcion de un comando) son validos o si no se 
        le han pasado parametros y el comando los requeria.
        

        Args:
            cmd (Command): Comando a procesar
            params (list): parametros que se le han pasado al comando

        Raises:
            CmdLineError: Si los parametros no son validos para el
                comando

        Returns:
            list: lista con los parametros del comando procesados. Si 
                se han proporcionado numeros en los parametros los 
                devuelve como int y no como str
        """
        if len(params) > 0:
            if not cmd.extra_arg:
                err_msg = (f"El comando '{cmd.name}' no admite " + 
                            f"parametros extra. Argumentos incorrectos " + 
                            f"-> {params}")
                raise CmdLineError(err_msg)
            elif len(params) > 1 and not cmd.multi: 
                err_msg = ("No se permite mas de 1 parametro extra " +
                          f"en el comando '{cmd.name}'. Argumentos " +
                          f"incorrectos -> {params[1:]}")
                raise CmdLineError(err_msg)
            extra_args = []
            for extra in params:
                try:
                    extra_args.append(int(extra))
                except:
                    extra_args.append(extra)
            if cmd.choices == None:
                return extra_args
            # Todos los extra args deben estar en choices
            for extra in extra_args:
                if extra not in cmd.choices:
                    break
            # Si completa el bucle es que todos son validos
            else:
                return extra_args
            err_msg = f"El parametro extra '{params[0]}' no es valido"
            raise CmdLineError(err_msg)
        elif not cmd.default == None:
            return [cmd.default]
        elif not cmd.mandatory:
            return []
        else:
            err_msg = f"El comando '{cmd.name}' requiere un parametro extra"
            raise CmdLineError(err_msg)
    
    def _check_flags(self, args:list, cmd:Command) -> list:
        """Revisa que los flags que se han proporcionado son 
        compatibles entre si

        Args:
            args (list): Linea de comandos a procesar

        Raises:
            CmdLineError: Si los comandos no son compatibles

        Returns:
            list: lista con los flags que habia en la linea de 
                de comandos proporcionada (args)
        """  
        flags = []
        gflags = list(self.global_flags.values())
        valid_flags = list(cmd.flags.values()) + gflags
        for arg in args: 
            for valid_flag in valid_flags:
                if arg == valid_flag.name:
                    if len(flags) > 0:
                        # Comprobamos que son flags compatibles
                        for flag in flags:
                            if (flag.name in valid_flag.ncwf or 
                                        valid_flag.name in flag.ncwf):
                                err_msg = (f"Los flags '{flag}' y " + 
                                         f"'{valid_flag}' no son compatibles")
                                raise CmdLineError(err_msg)
                    flags.append(valid_flag)
        # Eliminamos los flags ya procesadas de la linea de comandos  
        for flag in flags: args.remove(flag.name)
        # Guardamos los nombres de los flags en vez del objeto Flag
        # entero (ya no nos hace falta)
        flag_names = list(map(str, flags))
        # Vemos si se ha introducido un comando de ayuda
        if "-h" in flag_names:
            self.print_help(command=cmd); exit()
        elif "-ha" in flag_names:
            self.print_help(command=cmd, all_info=True); exit()
        elif "-hc" in flag_names:
            self.print_help(command=cmd, with_colors=True); exit()
        elif "-hca" in flag_names:
            self.print_help(
                command=cmd, with_colors=True, all_info=True
            ); exit()
        return flag_names
      
    def print_help(self, command=None, with_colors=False, 
                                    with_format=True, all_info=False):
        colorama.init()
        """Imprime las descripciones de cada comando y flag de la cli
        de forma estructurada"""
        # ------------------ Parametros a modificar ------------------
        maxline_length = 90; first_indent = 2; first_line_diff = 10
        gflags_indent = 4; nested_indent = first_indent + 6 
        nested_header_indent = first_indent + 3
        # -------------------- FUNCIONES INTERNAS --------------------
        def apply_shellformat(string:str, indent:int=4):
            return format_str(
                string, 
                maxline_length=maxline_length, 
                indent=indent, 
                tripleq_mode=True
            ) 
            
        def untab_firstline(string:str, indent:int):
            untabbed = ""
            index = string.find("\n")
            if index != -1:
                untabbed += string[:index] + "\n"
                if index < len(string) -1:
                    rest = string[index+1:]
                    untabbed += apply_shellformat(rest, indent=indent)
            else:
                untabbed = string
            return untabbed 
        
        def paint(line:str, color:str, 
                  with_colors=with_colors, with_format=with_format):
            if with_format:
                if with_colors:
                    return color + line + colors.ENDC
                elif color == colors.BOLD or color == colors.UNDERLINE:
                    return color  + line + colors.ENDC
            return line
        
        def _apply_predefined_format (string:str, extra_indent:int, 
                                      header:str, head_color:str, 
                                      nested=False, fixed_indent=None):
            if fixed_indent is None: 
                indent = first_indent
                if nested: indent = nested_indent
            else:
                indent = fixed_indent
            formatted = apply_shellformat(
                string, 
                indent=indent + extra_indent
            )
            formatted = untab_firstline(
                formatted, 
                indent=indent + first_line_diff + extra_indent
            )
            formatted = formatted.replace(
                header, 
                paint(paint(header, head_color), colors.BOLD), 
                1
            )
            return formatted
            
        def print_recursively(cmd:Command, i:int, max_iter:int=None):
            if max_iter is not None and i == max_iter: return
            nested_cmds = cmd.nested_cmds.values()
            nested_cmd_color = colors.OKCYAN
            extra_indent = (nested_indent-first_indent)*i
            if len(nested_cmds) > 0:
                print(
                    " "*(nested_header_indent+extra_indent) + "- " + 
                    paint("commands", colors.UNDERLINE) + ":"
                )
                for n_cmd in nested_cmds:
                    description = f"=> {n_cmd.name} "
                    if n_cmd.description is not None:
                        description += f"--> {n_cmd.description}"
                    formatted = _apply_predefined_format(
                        description, extra_indent, n_cmd.name, 
                        nested_cmd_color, nested=True
                    )
                    print(formatted)
                    print_recursively(n_cmd, i+1, max_iter=max_iter)
            for j in range(2):
                header = "options"
                array = cmd.options.values()
                elem_color = colors.OKBLUE
                if j == 1:
                    header = "flags"
                    array = cmd.flags.values()
                    elem_color = colors.OKGREEN
                if len(array) > 0:
                    print(
                        " "*(nested_header_indent+extra_indent) + "- " +
                        paint(header, colors.UNDERLINE) + ":"
                    )
                    for elem in array:
                        description = f"=> {elem.name} "
                        if elem.description is not None:
                            description += f"--> {elem.description}"
                        formatted = _apply_predefined_format(
                            description, extra_indent, elem.name, 
                            elem_color, nested=True
                        )
                        print(formatted)
                             
        # ------------------------------------------------------------ 
        if command is None:
            command = self.main_cmd
        print(paint(
            f"\n python3 {self.main_cmd} <parameters> <flags> <options> " + 
              "[command] <parameters> <flags> <options> [command] ...\n",
              colors.BOLD
        ))
        first_print_color = colors.WARNING
        # Comando
        description = f" => {command.name} "
        if command.description is not None:
            description += f"--> {command.description}"
        formatted = _apply_predefined_format(
            description, 0, command.name, first_print_color
        )
        print(formatted)
        max_iter = 1
        if all_info: max_iter = None
        print_recursively(command, 0, max_iter=max_iter)
        # Global Flags
        global_flags = self.global_flags.values()
        if len(global_flags) > 0:
            print(" + " + paint("Global Flags", colors.UNDERLINE) + ":")   
        for flag in global_flags:
            description = f"-> {flag.name} "
            if flag.description is not None:
                description += f"--> {flag.description}"
            formatted = _apply_predefined_format(
                description, 0, flag.name, first_print_color, 
                fixed_indent=gflags_indent
            )
            print(formatted)
        print() # Linea en blanco

# -------------------------------------------------------------------- 
class CmdLineError(Exception):
    """Excepcion personalizada para los errores de la cli"""
    def __init__(self, msg:str, help_=True):
        hlpm = "\nIntroduce el parametro -h para acceder a la ayuda" 
        msg = str(msg)
        if help_: msg += hlpm
        super().__init__(msg)
        
# --------------------------------------------------------------------
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# --------------------------------------------------------------------