import json


class RoadmapParser:
    def __init__(self, json_data):
        self.data = json_data
        self.mermaid_lines = []
        self.node_counter = {}

    def get_node_id(self, level, original_id):
        return original_id

    def add_class_definitions(self):
        self.mermaid_lines.append("classDef default fill:#f9f,stroke:#333,stroke-width:2px;")
        self.mermaid_lines.append("classDef alternative fill:#ccf,stroke:#333,stroke-width:1px;")
        self.mermaid_lines.append("classDef assignment fill:#fcc,stroke:#333,stroke-width:2px;")

    def generate_mermaid(self):
        self.mermaid_lines.append("graph TD")

        levels = self.data["graph"]["levels"]
        all_nodes = {}

        # First pass: nodes
        for level in levels:
            level_num = level["level"]
            for node in level["nodes"]:
                node_id = node["id"]
                content = node["content"]
                all_nodes[node_id] = {
                    "level": level_num,
                    "type": node.get("type", "compulsory"),
                    "content": content,
                }
                # Escape quotes in content
                safe_content = str(content).replace("\"", "\\\"")
                self.mermaid_lines.append(f'    {node_id}["{safe_content}"]')

        # Second pass: edges
        for level in levels:
            level_num = level["level"]
            if level_num == 0:
                continue
            for node in level["nodes"]:
                node_id = node["id"]
                prerequisites = node.get("longDescription", {}).get("prerequisites", [])
                if prerequisites:
                    for prereq in prerequisites:
                        edge = "-->" if node.get("type") == "compulsory" else "-.->"
                        self.mermaid_lines.append(f"    {prereq} {edge} {node_id}")
                else:
                    for prev_node_id, prev_node in all_nodes.items():
                        if prev_node["level"] == level_num - 1:
                            edge = "-->" if node.get("type") == "compulsory" else "-.->"
                            self.mermaid_lines.append(f"    {prev_node_id} {edge} {node_id}")

        self.add_class_definitions()
        for node_id, node in all_nodes.items():
            node_type = node.get("type")
            if node_type == "non-compulsory":
                self.mermaid_lines.append(f"class {node_id} alternative;")
            if node_type == "assignment":
                self.mermaid_lines.append(f"class {node_id} assignment;")

        return "\n".join(self.mermaid_lines)


def parse_roadmap(json_like):
    try:
        if isinstance(json_like, dict):
            json_data = json_like
        elif isinstance(json_like, str):
            try:
                with open(json_like, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except FileNotFoundError:
                json_data = json.loads(json_like)
        else:
            raise ValueError("Unsupported input type for roadmap JSON")

        parser = RoadmapParser(json_data)
        return parser.generate_mermaid()
    except Exception as e:
        return None


