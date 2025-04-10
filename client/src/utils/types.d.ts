export type Image = {
   file: File;
   url: string;
   name: string;
   size: number;
   width: number;
   height: number;
};

export type ImageToProcess = {
   model: string;
   factor: string;
   image: Image;
};

export type ServerMessage = {
   statusCode: number;
   status: string;
   message: string;
   data?: any;
};
