![main branch CI status](https://github.com/NyuB/py_java_package_info/actions/workflows/ci.yml/badge.svg?branch=main)
# Check and generate package-info.java

## Usage

### Check
**check** : exit with error code 1 if some package-info.java are missing

`python3 package_info.py check <sources-root>`

```bash
python3 package_info.py check src/main.java
```

### Generate

#### All
**set-all** : replace already present and generate missing package info from template

`python3 package_info.py set-all <sources-root> <template-file>`

```bash
$> python3 package_info.py set-all src/main/java my-template.txt
```

#### Only missing
**set-missing** : only generate missing package info from template

`python3 package_info.py set-all <sources-root> <template-file>`

```bash
$> python3 package_info.py set-missing src/test/kotlin template.txt
```

#### Template file

The template file must follow the python3 [string.Template()](https://docs.python.org/3.4/library/string.html#template-strings) syntax and can use one template argument named `package` which will receive the relevant fully qualified java package name.

Example:

```
package ${package};
// My awesome java package info for ${package}
```

would be replaced by

```
package com.my.awesome.package;
// My awesome java package info for com.my.awesome.package
```

in the folder `<sources-root>/com/my/awesome/package/`
