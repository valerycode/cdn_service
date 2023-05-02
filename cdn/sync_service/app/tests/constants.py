put_to_master_event = {
    "Records": [
        {
            "eventName": "s3:ObjectCreated:Put",
            "s3": {
                "object": {
                    "key": "3c1f4e7e-3375-4f11-a3f9-e735d3f5ae8e",
                    "size": 15,
                },
            },
            "source": {"host": "172.18.0.10"},
        }
    ],
}

put_to_edge_event = {
    "Records": [
        {
            "eventName": "s3:ObjectCreated:Put",
            "s3": {
                "object": {
                    "key": "3c1f4e7e-3375-4f11-a3f9-e735d3f5ae8e",
                    "size": 15,
                },
            },
            "source": {"host": "172.18.0.11"},
        }
    ],
}
