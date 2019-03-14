/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   liblist.h                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marvin <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/03/14 13:42:25 by marvin            #+#    #+#             */
/*   Updated: 2019/03/14 13:55:07 by marvin           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

/*
**	An opinionated list implementation, in the questionable code style of École 42.
**
**
**	      doubly_linked_list_t             doubly_linked_element_container_t
**
**	+-------------------------+          +-------------+-------+     
**	|                         |          |               next +-----> NULL
**	|                    head +--------->+   content           |
**	|  size                   |          |               prev  |
**	|                         |          +---------------^-----+
**	|                    tail +----+                     |  |
**	|                         |    |     +---------------+--v--+
**	+-------------------------+    |     |               next  |
**	                               |     |   content           |
**	                               |     |               prev  |
**	                               |     +---------------^-----+
**	                               |                     |  |
**	                               |     +---------------+--v--+
**	                               |     |               next  |
**	                               +---->+   content           |
**	                                     |               prev +-----> NULL
**	                                     +---------------------+
**
*/

#ifndef LIBLIST_H
# define LIBLIST_H

#include <stdlib.h>

typedef struct	doubly_linked_element_container_s
{
	struct doubly_linked_element_container_s	*next;
	struct doubly_linked_element_container_s	*prev;
	void										*element;
}				doubly_linked_element_container_t;

typedef struct	doubly_linked_list_s
{
	doubly_linked_element_container_t			*head;
	doubly_linked_element_container_t			*tail;
	size_t							size;
}				doubly_linked_list_t;

int				list_is_empty(doubly_linked_list_t *list);
void			list_prepend(doubly_linked_list_t *list, void *element);
void			list_append(doubly_linked_list_t *list, void *element);
doubly_linked_list_t *new_doubly_linked_list();
doubly_linked_element_container_t *new_doubly_linked_element_container();
void delete_doubly_linked_list(doubly_linked_list_t *list,
			   void del(void *element));

#endif
