from django.shortcuts import render
from transcode.models import Node
from django.db.models import Count

# Create your views here.

nodes = Node.objects.values('trans_code').annotate(counts=Count('trans_code'))

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


def index(request):
    return render(request, "transcode/index.html", {"nodes": nodes})


def trans_code(request, transcode):
    return render(request, "transcode/node_set.html", {"transcode": transcode, "nodes": nodes})
