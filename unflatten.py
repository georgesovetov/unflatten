import functools


def transform_result(transform_func):
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            return transform_func(f(*args, **kwargs))

        return decorated

    return decorator


def _try_to_parse_int(item):
    try:
        return int(item)
    except ValueError:
        return item


@transform_result(''.join)
@transform_result(lambda t: (str(i) for i in t))
def brackets_join(split_items):
    yield split_items[0]
    for item in split_items[1:]:
        yield '['
        yield item
        yield ']'


@transform_result(lambda t: tuple(_try_to_parse_int(i) for i in t))
def brackets_split(joined_items):
    try:
        first_bracket_pos = joined_items.index('[')
    except ValueError:
        yield joined_items
    else:
        yield joined_items[:first_bracket_pos]
        for item in joined_items[first_bracket_pos + 1:-1].split(']['):
            yield item


@transform_result(''.join)
def dot_colon_join(split_items):
    yield split_items[0]
    for item in split_items[1:]:
        if isinstance(item, int):
            yield ':'
            yield str(item)
        else:
            yield '.'
            yield item


@transform_result(tuple)
def dot_colon_split(joined_items):
    for dot_separated_item in joined_items.split('.'):
        dot_colon_separated_items = dot_separated_item.split(':')
        yield dot_colon_separated_items[0]
        for dot_colon_separated_item in dot_colon_separated_items[1:]:
            yield int(dot_colon_separated_item)


def _tree_to_path_tuples_with_values(tree):
    if isinstance(tree, (list, tuple)):
        for sub_tree_index, sub_tree in enumerate(tree):
            for key_path, value in _tree_to_path_tuples_with_values(sub_tree):
                yield (sub_tree_index,) + (key_path), value
    elif isinstance(tree, dict):
        for sub_tree_key, sub_tree in tree.items():
            for key_path, value in _tree_to_path_tuples_with_values(sub_tree):
                yield (sub_tree_key,) + (key_path), value
    elif isinstance(tree, (int, float, str, None)):
        yield (), tree
    else:
        assert False, "Unexpected type in tree"


def _insert_into_dict_tree_by_path_tuple(path, value, tree):
    if len(path) == 1:
        tree[path[0]] = value
    else:
        if path[0] not in tree:
            tree[path[0]] = {}
        _insert_into_dict_tree_by_path_tuple(path[1:], value, tree[path[0]])


def _recognize_lists(tree):
    if not isinstance(tree, dict):
        return tree
    else:
        if set(tree.keys()) == set(range(len(tree))):
            return [_recognize_lists(tree[index]) for index in range(len(tree))]
        else:
            return {key: _recognize_lists(tree[key]) for key in tree}


def _path_tuples_with_values_to_dict_tree(flat_tree):
    tree = {}
    for path, value in flat_tree:
        _insert_into_dict_tree_by_path_tuple(path, value, tree)
    return tree


def flatten(tree, join=brackets_join):
    return {join(tuple_path): value
            for tuple_path, value
            in _tree_to_path_tuples_with_values(tree)}


def unflatten(flat_tree, split=brackets_split):
    return _recognize_lists(
        _path_tuples_with_values_to_dict_tree(
            (split(path), value) for path, value in flat_tree.items()))
