#include <cstring>   // strdup, strcmp
#include <cstdio>
#include <cassert>

struct Node {
  ~Node() {
    free((void*)value);
  }

  const char* value = nullptr;
  Node* prev = nullptr;
  Node* next = nullptr;
};

struct List {
  ~List();
  void insert(const char* s);
  const char* find(const char* s);
  bool remove(const char* s);

  Node* start_ = nullptr;
  Node* end_ = nullptr;
  size_t size_ = 0;
};

List::~List() {
  while (start_) {
    auto cp = start_;
    start_ = start_->next;
    delete cp;
  }
}

void List::insert(const char* s) {
  Node* node = new Node();
  node->value = strdup(s);

  if (size_ == 0) {
    start_ = node;
    end_ = node;
  } else {
    end_->next = node;
    node->prev = end_;
    end_ = node;
  }
  ++size_;
}

const char* List::find(const char* s) {
  auto start = start_;
  while (start) {
    if (strcmp(start->value, s) == 0) {
      return start->value;
    }
    start = start->next;
  }
  return nullptr;
}

bool List::remove(const char* s) {
  Node* back = nullptr;
  auto start = start_;
  while (start) {
    if (strcmp(start->value, s) == 0) {
      if (start == start_) {
        assert(back == nullptr);
        start_ = start->next;
        start_->prev = nullptr;
      } else if (start == end_) {
        assert(back != nullptr);
        end_ = back;
        end_->next = nullptr;
      } else {
        assert(back != nullptr);
        back->next = start->next;
        start->next->prev = back;
      }
      delete start;
      return true;
    }
    back = start;
    start = start->next;
  }

  return false;
}



int main() {
  List list;
  list.insert("this");
  list.insert("is");
  list.insert("first");
  list.insert("program");

  list.remove("this");
  list.remove("first");
  list.remove("program");
}
