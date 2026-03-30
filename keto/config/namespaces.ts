import { Context, Namespace } from "@ory/keto-namespace-types";

class User implements Namespace {}

class Document implements Namespace {
  related: {
    readers: User[];
    editors: User[];
    owners: User[];
  };

  permits = {
    read: (ctx: Context): boolean =>
      this.related.readers.includes(ctx.subject) ||
      this.related.editors.includes(ctx.subject) ||
      this.related.owners.includes(ctx.subject),

    edit: (ctx: Context): boolean =>
      this.related.editors.includes(ctx.subject) ||
      this.related.owners.includes(ctx.subject),

    delete: (ctx: Context): boolean =>
      this.related.owners.includes(ctx.subject),
  };
}
