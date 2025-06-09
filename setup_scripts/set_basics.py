

# This scripts gets path to a .py file
# and adds autolog to each fn, 
# log_stack to each fn body's except condition
# log_locals to before each return statement.


# It also goes and removes all such lines, given --rem

# You have to already have the pylog preamble addd manually 
# (they change too often and can have lines switched and such,
#  so we can't check it's not there, and threfore can't ad it 
# automatically because we would keep adding it on all runs)
# It needs to make MY_LOGGER available in the file.




# python3 -m python_logger.setup_scripts.set_basics sysrun/bashpy_boilerplate/diplomska_boilerplate.py
# --rem

import argparse
from pathlib import Path




parser = argparse.ArgumentParser()
parser.add_argument("path_to_file", type=str) #, required=True)
parser.add_argument("--rem", action="store_true", default=False, help="remove all such things from the file.")

args = parser.parse_args()





DEBUG = False
DEBUG_BLOCK = 13


def main():

    path = Path(args.path_to_file)
    if not path.is_dir():
        handle_file(path)
    else:
        # recurse for all files in the directory
        print(f"Recursing into directory {path}.")
        for file in path.glob("**/*.py"):
            handle_file(file)





def handle_file(path_to_file):
    if args.rem:
        print("Removing all autolog, log_stack and log_locals lines from the file.")




        if not path_to_file.exists():
            raise FileNotFoundError(f"File {path_to_file} does not exist.")
        if not path_to_file.is_file():
            raise ValueError(f"Path {path_to_file} is not a file.")
        if not path_to_file.suffix == ".py":
            raise ValueError(f"Path {path_to_file} is not a .py file.")
        

        with open(path_to_file, "r") as f:
            content = f.read()
            lines = content.split("\n")


        # remove autologs
        lines = [line for line in lines if not line.strip().startswith("@py_log.autolog(")]
        # remove log_locals
        lines = [line for line in lines if not line.strip().startswith("py_log.log_locals(MY_LOGGER)")]

        # We just keep log stack for now.
        # removing would be a pain in the ass, because removing the whole try: except, and de-indenting
        # And doesn't make sense, because it never gets triggered anyway - only upon exceptions.
        # So doesn't clutter logs and doesn't waste time, so noone cares.
        # remove log_stack
        # lines = [line for line in lines if not line.strip().startswith("py_log.log_stack(")]

        full_file = "\n".join(lines)

        with open(path_to_file, "w") as f:
            f.write(full_file)



        

    else:
        print("Adding autolog, log_stack and log_locals to the file.")
        
        if not path_to_file.exists():
            raise FileNotFoundError(f"File {path_to_file} does not exist.")
        if not path_to_file.is_file():
            raise ValueError(f"Path {path_to_file} is not a file.")
        if not path_to_file.suffix == ".py":
            raise ValueError(f"Path {path_to_file} is not a .py file.")
        


        with open(path_to_file, "r") as f:
            content = f.read()
            lines = content.split("\n")

            if DEBUG:
                for i, line in enumerate(lines):
                    print(f"{i}: {line}")



            # build the fn blocks (including the decorator of the fn)
            # A problem we have is, that fns can have fn defs nested in them (fns on the fly)
            # We therefore have to go by indentation.
            # When we find a def, we know we remain in that fn until indentation falls below the fn indentation.

            # We will first only check for unnested fns.
            # Later, we might recurse and do the same for nested fns, but that is not needed now.

            # We also musnt't forget that the decorators before an fn block belong to the fn block.

            def handle_non_fn_code_block(lines, line_ix):
                """
                Handle a block of code that is not a function definition.
                This will be used to handle the code before the first function definition.
                And in between fn definitions.

                It basically stops before it sees a decorator or a function definition.

                Returns the line_ix after the block of code. So indexing later should be easy.
                """
                line_striped = lines[line_ix].strip()
                if (line_striped.startswith("@") or line_striped.startswith("def ")):
                    # If we are already at a decorator or a function definition, 
                    # we don't need to handle this.
                    return line_ix

                curr_line_ix = line_ix
                while curr_line_ix < len(lines):
                    line = lines[curr_line_ix]
                    stripped_line = line.strip()
                    if stripped_line.startswith("@") or stripped_line.startswith("def "):
                        # We reached a decorator or a function definition, stop here.
                        return curr_line_ix
                    curr_line_ix += 1
                return curr_line_ix
            

            def handle_fn_def(lines, line_ix):
                """
                Juast handle the decorators and defs.
                """


                curr_line_ix = line_ix
                while curr_line_ix < len(lines):
                    line_striped = lines[curr_line_ix].strip()
                    if not (line_striped.startswith("@") or line_striped.startswith("def ")):
                        # We reached a line that is not a decorator or a function definition, stop here.
                        return curr_line_ix
                    
                    curr_line_ix += 1
                return curr_line_ix

            def handle_fn_body(lines, line_ix, indentation):
                """
                Handle a block of code that is a function.
                Ignore nested fns for now.
                We simply go for as long as the indentation is the same as the fn indentation.
                
                Returns the line_ix after the fn stop. So indexing later should be easy.
                """
                curr_line_ix = line_ix
                while curr_line_ix < len(lines):
                    line_l_striped = lines[curr_line_ix].lstrip()
                    if not line_l_striped:  # empty lines cause problems, so we glob them.
                        curr_line_ix += 1
                        continue
                    ind = len(lines[curr_line_ix]) - len(line_l_striped)
                    if ind < indentation:
                        # We reached a line with less indentation than the fn indentation, stop here.
                        return curr_line_ix
                    
                    curr_line_ix += 1
                return curr_line_ix
            
            def handle_fn(lines, line_ix):

                # First handle decorators and def
                def_new_line_ix = handle_fn_def(lines, line_ix)

                # Then handle the body.
                # ind = len(lines[def_new_line_ix]) - len(lines[def_new_line_ix].lstrip()) # if empty line after def, this will be 0 and cause a bug.
                last_def_line_ix = lines[def_new_line_ix-1]
                def_line_ind = len(last_def_line_ix) - len(last_def_line_ix.lstrip()) # So rather get the def ind, and add 1 as the limit of the inner block ind.
                body_new_line_ix = handle_fn_body(lines, def_new_line_ix, def_line_ind+1) # +1 because we want to include all body lines, which are defined as being indented at least one more than the def line.
                
                return def_new_line_ix, body_new_line_ix
            



            code_block_ixs = []
            line_ix = 0
            while line_ix < len(lines):
                if DEBUG:
                    print(line_ix)
                new_line_ix = handle_non_fn_code_block(lines, line_ix)
                if new_line_ix != line_ix: # this will happen if no regular code block was found (we are at th start of an fn).
                    # We found a block of code that is not a function definition.
                    code_block_ixs.append((line_ix, new_line_ix, "not_fn"))
                    line_ix = new_line_ix
                    continue
                # We are at a decorator or a def.
                def_new_line_ix, body_new_line_ix = handle_fn(lines, line_ix)
                code_block_ixs.append((line_ix, def_new_line_ix, "def_fn"))
                code_block_ixs.append((def_new_line_ix, body_new_line_ix, "body_fn"))
                line_ix = body_new_line_ix



            
            code_blocks = []
            for start, end, block_type in code_block_ixs:

                block_lines = lines[start:end].copy()
                block_text = "\n".join(block_lines)

                if DEBUG:
                    print(start, end, block_type)
                    for i in range(start, end):
                        print(f"{i}: {lines[i]}")

                    
                    print(f"Block lines: {block_lines}")


                def get_leading_whitespace(line):
                    """
                    Get the leading whitespace of a line.
                    """
                    def_indent = len(line) - len(line.lstrip())
                    indent_text = line[:def_indent] # get the leading whitespace.
                    return indent_text
                
                def get_first_nonempty_line_ix(block_lines):
                    """
                    Get the first non-empty line from the lines starting at start_ix.
                    """
                    for i in range(len(lines)):
                        if block_lines[i]:
                            return i
                    return None
                

                if block_type == "not_fn":
                    # Just add the block as is.
                    code_blocks.append(block_lines)
                elif block_type == "def_fn":
                    # def_fn block has: decorators and the def line.
                    # The last line is sure to be the def line.
                    # We need to add the autolog decorator.
                    # We need to add it right before the def line:
                    # so that we autolog the actual fn, not the encompasing decorator
                    # (decorators are just syntactic sugar for nesting a function inside the decorator function).

                    if not "@py_log.autolog(passed_logger=MY_LOGGER)" in block_text:
                        # Add autolog to the def line
                        block_lines.insert(-1, f"{get_leading_whitespace(block_lines[-1])}@py_log.autolog(passed_logger=MY_LOGGER)")
                    code_blocks.append(block_lines)



                elif block_type == "body_fn":

                    # If not ending in except: log_stack, we encompass the whole block in a try block, and the final except block.
                    if not "py_log.log_stack(MY_LOGGER)" in block_text:
                        line_ix = get_first_nonempty_line_ix(block_lines)
                        indent_whitespace = get_leading_whitespace(block_lines[line_ix])
                        # indent all body lines by 4 spaces
                        block_lines = [f"    {line}" for line in block_lines]
                        # add try:
                        block_lines.insert(0, f"{indent_whitespace}try:")
                        # add except Exception as e: py_log.log_stack(MY_LOGGER) raise e
                        block_lines.extend([f"{indent_whitespace}except Exception as e:",
                                            f"{indent_whitespace}    py_log.log_stack(MY_LOGGER)",
                                            f"{indent_whitespace}    raise e"])
                    
                    # in front of all returns, we add log_locals.
                    for i in range(len(block_lines)-1, -1, -1):
                        # we go in reverse so we can easily insert and not have other return ixes change.
                        line = block_lines[i]
                        if "return " in line:
                            # Add log_locals before return statement
                            block_lines.insert(i, f"{get_leading_whitespace(line)}py_log.log_locals(MY_LOGGER)")


                    # Add the body of the fn.
                    code_blocks.append(block_lines)
                else:
                    raise ValueError(f"Unknown block type: {block_type}")


            if DEBUG:
                for i, block in enumerate(code_blocks):              

                    if False:
                        if i > 4:
                            break

                    print(10*"\n" + f"Block {i}:\n")
                    for line in block:
                        print(line)
            

            full_file = ""
            for block in code_blocks:
                full_file += "\n".join(block) + "\n\n"

            if DEBUG:
                path_to_file = Path("temp.py")
            with open(path_to_file, "w") as f:
                f.write(full_file)


if __name__ == "__main__":
    main()