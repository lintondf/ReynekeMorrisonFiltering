/**
 * 
 */
package com.bluelightning.tools.transpiler.nodes;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.apache.commons.lang3.StringUtils;


/**
 * @author NOOK
 *
 */
public class TranslationNode  {
	
	protected String name;
	private String type;

	protected TranslationNode parent;
	protected List<TranslationNode> children;
	
	TranslationNode( TranslationNode parent, String name) {
		this.name = name;
		this.type = "int";
		this.parent = parent;
		this.children = new ArrayList<>();
		if (parent != null) {
			parent.children.add(this);
		}
	}
	
	public String getType() {
		return type;
	}
	
	final static List<String> precedence = Arrays.asList(new String[] {"int", "float", "vector", "array"});
	
	public void setType(String type) {
		int currentIndex = precedence.indexOf(this.type);
		int typeIndex = precedence.indexOf(type);
		if ( typeIndex >= 0 && currentIndex >= 0) {
			if (typeIndex > currentIndex) {
				this.type = type;
			}
		} else {
			this.type = type;
		}
		if (parent != null) {
			parent.setType(this.type);
		}
	}
	
	public String traverse( int indent ) {
		StringBuffer sb = new StringBuffer();
		if (this.getTop() instanceof TranslationExpressionNode) {
			TranslationExpressionNode ten = (TranslationExpressionNode) this.getTop();
			sb.append( ten.getParserRuleContext().getText() );
		}
		String spaces = String.format("%5d:%s", indent, StringUtils.repeat("  ", indent));
		sb.append(spaces);
		sb.append( this.toString() );
		sb.append('\n');
		for (TranslationNode child : children) {
			sb.append( child.traverse(indent+1) );
		}
		return sb.toString();		
	}
	
	public String toString() {
		return String.format("[%d] %s ", children.size(), name );
//		return name + " C#" + children.size() + ((parent == null) ? "?" : parent.toString());
	}

	public void adopt(TranslationNode node) {
		if (node.parent != null) {
			node.parent.removeChild(node);
		}
		node.parent = this;
		this.children.add(node);
		this.setType( node.getType() );
	}
	
	public void replace( TranslationNode node ) {
		if (node.parent != null) {
			node.parent.removeChild(node);
		}
		node.parent = this;
		this.type = node.type;
		this.children = node.children;
	}
	
    public void addChild(TranslationNode node ) {
    	node.parent = this;
    	children.add(node);
    	this.setType( node.getType() );
    }
    
	public void removeChild(TranslationNode node) {
		children.remove(node);
	}
	
	public List<TranslationNode> getChildren() {
		return children;
	}

	public int getChildCount() {
		return children.size();
	}

	public TranslationNode getChild(int i) {
		return children.get(i);
	}
	
	public TranslationNode getLastChild() {
		if (children.isEmpty())
			return null;
		return children.get( children.size()-1 );
	}
	
	public TranslationNode getParent() {
		return parent;
	}
	
	public TranslationNode getTop() {
		TranslationNode node = this;
		while (node.getParent() != null) {
			node = node.getParent();
		}
		return node;
	}

	public TranslationNode getFirstChild() {
		if (children.isEmpty())
			return null;
		return children.get(0);
	}

	public TranslationNode getLeftSibling() {
		int i = parent.children.indexOf(this);
		if (i <= 0) {
			return null;
		}
		return parent.children.get(i-1);
	}
	
	public TranslationNode getRightSibling() {
		int i = parent.children.indexOf(this);
		if (i >= parent.children.size()-1) {
			return null;
		}
		return parent.children.get(i+1);
	}
	
	public String getName() {
		return name;
	}

	
}
