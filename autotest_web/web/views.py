from django.shortcuts import render

import os, sys, django

# print(sys.path)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autotest_web.settings')
# django.setup()


from web.models import Node

# Create your views here.


def insert(kwargs):
    product_node_value = kwargs["product_node"]
    real_node_value = kwargs["real_node"]
    case_id_value = kwargs["case_id"]
    trans_code_value = kwargs["trans_code"]
    node_value_value = kwargs["node_value"]

    n = Node(product_node=product_node_value, real_node=real_node_value, case_id=case_id_value,
             trans_code=trans_code_value, node_value=node_value_value)

    n.save()
    print("success insert data into database, data id is %d" % n.id)


def search(id):
    node = Node.objects.get(id=id)
    print(node.product_node, node.real_node, node.node_value)


def delete(id):
    node = Node.objects.get(id=id)
    node.delete()
    print("delete success")


def update(id, **kwargs):
    node = Node.objects.get(id=id)
    for k,v in kwargs:
        if k == "product_node":
            node.product_node = v
        elif k == "real_node":
            node.real_node = v
        elif k == "node_value":
            node.node_value = v
        else:
            print("更新异常")
    node.save()


def print_all():
    nodes = Node.objects.all()
    for node in nodes:
        print(node.id)
        print(node.product_node)
        print(node.real_node)
        print(node.node_value)


def test(request, year):
    return render(request, 'new.html')


def index(request):
    return render(request, 'test.html')


if __name__ == "__main__":
    test = {"product_node":"/hupp/test", "real_node":"/real/test", "case_id":"02", "trans_code":"961001", "node_value":"测试"}
    insert(test)
    print_all()